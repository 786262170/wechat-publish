#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号发布管线 · 健康检查 + 首次使用引导

检查 6 项，任何一项失败都会给出对应的修复指引：
  1. PicGo 是否安装
  2. PicGo Server 是否监听（默认 127.0.0.1:36677）
  3. 图床是否已配置（读 PicGo 配置）
  4. GitHub token 是否有效（若图床为 github/githubPlus）
  5. 图床仓库是否可访问
  6. 图床仓库的存储路径（如 img/）是否已存在

用法：
  python3 doctor.py            # 只检查，打印报告
  python3 doctor.py --fix-img  # 检查后，若 img/ 目录缺失则尝试自动创建（需 gh 或 token）

退出码：0 = 全部就绪；1 = 有未就绪项
"""
import json
import os
import sys
import platform
import urllib.request
import urllib.error
from pathlib import Path

PICGO_SERVER = os.environ.get("PICGO_SERVER", "http://127.0.0.1:36677")


def picgo_config_path() -> Path:
    """跨平台定位 PicGo 配置文件 data.json。"""
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "picgo" / "data.json"
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "picgo" / "data.json" if appdata else None
    # Linux
    return Path.home() / ".config" / "picgo" / "data.json"


def check_picgo_installed():
    sysname = platform.system()
    if sysname == "Darwin":
        ok = Path("/Applications/PicGo.app").exists()
        hint = "brew install --cask picgo"
    elif sysname == "Windows":
        ok = Path(os.environ.get("LOCALAPPDATA", ""), "Programs", "PicGo").exists()
        hint = "从 https://picgo.github.io/PicGo-Doc/ 下载安装"
    else:
        ok = Path("/usr/share/applications/picgo.desktop").exists() or Path.home().joinpath("Applications").exists()
        hint = "从 https://picgo.github.io/PicGo-Doc/ 下载 AppImage"
    return ok, hint


def check_server():
    """PicGo Server 是否在监听。用 GET 探活（PicGo Server 对 GET 返回 404 或空，但连接能建立即说明在监听）。"""
    try:
        req = urllib.request.Request(PICGO_SERVER + "/", method="GET")
        urllib.request.urlopen(req, timeout=3)
        return True, None
    except urllib.error.HTTPError:
        # 有 HTTP 响应 = 服务在监听（只是这个路径没实现）
        return True, None
    except Exception as e:
        return False, f"无法连接 {PICGO_SERVER}（{e.__class__.__name__}）"


def load_picgo_config():
    path = picgo_config_path()
    if not path or not path.exists():
        return None, str(path)
    try:
        return json.loads(path.read_text(encoding="utf-8")), str(path)
    except Exception as e:
        return None, f"配置文件读取失败：{e}"


def check_bed_configured(config):
    """图床是否已配置。返回 (ok, current_type, detail)。"""
    picbed = config.get("picBed", {})
    current = picbed.get("current") or picbed.get("uploader")
    if not current:
        return False, None, "未选择图床"
    bed_cfg = picbed.get(current, {})
    if not bed_cfg:
        return False, current, f"图床 {current} 无配置"
    # 通用：至少要有 token / repo 之类的关键字段
    if current in ("github", "githubPlus"):
        need = ["repo", "branch", "token"]
        missing = [k for k in need if not bed_cfg.get(k)]
        if missing:
            return False, current, f"缺少字段：{', '.join(missing)}"
        return True, current, f"repo={bed_cfg.get('repo')}"
    # 其他图床：只要配置段非空即视为已配置（不做字段级校验）
    return True, current, "已配置"


def check_github_token(bed_cfg):
    token = bed_cfg.get("token", "")
    if not token:
        return False, "无 token"
    try:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}", "User-Agent": "wechat-publish-doctor"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        login = data.get("login")
        return bool(login), f"登录用户 {login}" if login else f"token 无效：{data.get('message')}"
    except Exception as e:
        return False, f"验证失败：{e}"


def check_github_repo(bed_cfg):
    repo = bed_cfg.get("repo", "")
    token = bed_cfg.get("token", "")
    if not repo:
        return False, "未配置 repo"
    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"token {token}", "User-Agent": "wechat-publish-doctor"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("full_name"):
            return True, f"{data.get('full_name')} ({data.get('visibility')})"
        return False, f"仓库不存在或无权限：{data.get('message')}"
    except Exception as e:
        return False, f"检查失败：{e}"


def check_storage_path(bed_cfg):
    """检查图床存储路径（如 img/）是否已在仓库中存在。github-plus 要求预先存在。"""
    repo = bed_cfg.get("repo", "")
    token = bed_cfg.get("token", "")
    path = (bed_cfg.get("path") or "img/").strip("/")
    if not repo:
        return False, "未配置 repo", None
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"token {token}", "User-Agent": "wechat-publish-doctor"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
        return True, f"{path}/ 已存在", (repo, token, path)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, f"{path}/ 目录不存在（github-plus 插件要求预先创建）", (repo, token, path)
        return False, f"检查失败：HTTP {e.code}", (repo, token, path)
    except Exception as e:
        return False, f"检查失败：{e}", (repo, token, path)


def fix_storage_path(info):
    """通过 GitHub API 创建占位文件，从而创建目录。info = (repo, token, path)。"""
    repo, token, path = info
    url = f"https://api.github.com/repos/{repo}/contents/{path}/.gitkeep"
    payload = json.dumps({"message": "init: seed storage directory", "content": "Cg=="}).encode()
    req = urllib.request.Request(
        url, data=payload, method="PUT",
        headers={"Authorization": f"token {token}", "User-Agent": "wechat-publish-doctor",
                 "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("content", {}).get("path") is not None
    except Exception as e:
        print(f"  ✗ 自动创建失败：{e}")
        return False


def main():
    print("=" * 56)
    print("公众号发布管线 · 健康检查")
    print("=" * 56)

    results = []
    bed_cfg = None
    current_type = None

    # 1. PicGo 安装
    ok, hint = check_picgo_installed()
    results.append(ok)
    print(f"\n[1/6] PicGo 安装          {'✓' if ok else '✗'}")
    if not ok:
        print(f"      → 安装命令：{hint}")

    # 2. Server 监听
    ok, err = check_server()
    results.append(ok)
    print(f"[2/6] PicGo Server 监听    {'✓' if ok else '✗'}  ({PICGO_SERVER})")
    if not ok:
        print("      → PicGo 设置 → 设置 Server → 开启「Server」（端口 36677）")
        print("      → 确保 PicGo 正在运行")
        print(f"      → 原始错误：{err}")

    # 3. 图床配置
    config, cfg_path = load_picgo_config()
    if config is None:
        results.append(False)
        print(f"[3/6] 图床配置            ✗  （配置文件：{cfg_path}）")
        print("      → 打开 PicGo → 图床设置 → 选择图床（如 GitHub）并填写")
    else:
        ok, current_type, detail = check_bed_configured(config)
        results.append(ok)
        print(f"[3/6] 图床配置            {'✓' if ok else '✗'}  （图床类型：{current_type or '无'}）")
        if ok and detail:
            print(f"      → {detail}")
        elif not ok:
            print(f"      → {detail}")
        if current_type:
            bed_cfg = config.get("picBed", {}).get(current_type, {})

    # 4~6 仅当图床是 github 系列时做深度检查
    if current_type in ("github", "githubPlus") and bed_cfg:
        ok, detail = check_github_token(bed_cfg)
        results.append(ok)
        print(f"[4/6] GitHub token 有效    {'✓' if ok else '✗'}  （{detail}）")
        if not ok:
            print("      → https://github.com/settings/tokens 生成 token，勾选 repo 权限")

        ok, detail = check_github_repo(bed_cfg)
        results.append(ok)
        print(f"[5/6] 图床仓库可访问      {'✓' if ok else '✗'}  （{detail}）")
        if not ok:
            print("      → 确认仓库名正确，且 token 有该仓库权限")

        ok, detail, fix_info = check_storage_path(bed_cfg)
        results.append(ok)
        print(f"[6/6] 存储路径就绪        {'✓' if ok else '✗'}  （{detail}）")
        if not ok and fix_info and "--fix-img" in sys.argv:
            print("      → 尝试自动创建存储目录……")
            if fix_storage_path(fix_info):
                print("      → ✓ 已创建，重新运行 doctor.py 验证")
                results[-1] = True
            else:
                print("      → 手动创建：在仓库里建一个空目录，或用 git 提交一个 .gitkeep")
        elif not ok:
            print("      → 加 --fix-img 自动创建，或手动在仓库里建该目录（github-plus 要求预先存在）")
    elif current_type:
        print("\n[4/6][5/6][6/6] 跳过（当前图床非 GitHub，无法做深度检查）")

    print("\n" + "=" * 56)
    if all(results):
        print("✓ 全部就绪！可直接运行 auto-publish.py")
        code = 0
    else:
        failed = sum(1 for r in results if not r)
        print(f"✗ 有 {failed} 项未就绪，请按上方指引修复后重跑本脚本。")
        code = 1
    print("=" * 56)
    sys.exit(code)


if __name__ == "__main__":
    main()

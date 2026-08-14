#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号图片「一键上传 + 替换」脚本（需 PicGo 配合）

前置条件：
  1. 安装并配置好 PicGo（图床选好，能正常上传）
  2. 开启 PicGo Server：PicGo 设置 → 设置 Server → 打开（默认 127.0.0.1:36677）
  3. 确保 PicGo 正在运行

用法：
  # 方式一：显式传参（推荐，通用）
  python3 auto-publish.py <排版HTML> <图片目录> <img1.png,img2.png,...>

  # 方式二：从 HTML 自动推断占位符（图片目录里按 __IMAGE_N__ 顺序放图）
  python3 auto-publish.py <排版HTML> <图片目录>

  # 方式三：环境变量配置默认路径（个人复用）
  export WECHAT_VAULT="/path/to/vault"
  export WECHAT_HTML="03_草稿/xxx.html"
  export WECHAT_ASSETS="06_素材库/xxx配图"
  export WECHAT_IMAGES="img1.png,img2.png"
  python3 auto-publish.py

脚本会自动：
  1. 调用 PicGo Server 上传图片
  2. 拿图床 URL 替换 HTML 里的 __IMAGE_N__ 占位符
  3. 输出 *_final.html
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

PICGO_SERVER = os.environ.get("PICGO_SERVER", "http://127.0.0.1:36677/upload")


def upload_via_picgo(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"图片不存在：{path}")
    payload = json.dumps({"list": [str(path)]}).encode("utf-8")
    req = urllib.request.Request(
        PICGO_SERVER, data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"\n✗ 无法连接 PicGo Server（{PICGO_SERVER}）。")
        print("  请确认：1) PicGo 正在运行；2) 已在设置中开启 Server。")
        print(f"  原始错误：{e}\n")
        sys.exit(1)
    if not data.get("success") or not data.get("result"):
        raise RuntimeError(f"PicGo 返回上传失败：{data}")
    return data["result"][0]


def discover_placeholders(src_html: Path, asset_dir: Path):
    """从 HTML 里找 __IMAGE_N__ 占位符，按顺序映射到图片目录里的文件。"""
    html = src_html.read_text(encoding="utf-8")
    placeholders = sorted(set(re.findall(r"__IMAGE_(\d+)__", html)), key=int)
    if not placeholders:
        print("✗ HTML 里没有找到 __IMAGE_N__ 占位符。")
        sys.exit(1)

    # 尝试按占位符数字匹配目录里的文件（img_1.png / 1.png 等），否则用目录下全部 PNG 排序
    pngs = sorted(asset_dir.glob("*.png"))
    filenames = []
    for n in placeholders:
        candidates = [
            p.name for p in pngs
            if re.match(rf"(?:img[-_]?)?{n}\.png$", p.name, re.I)
        ]
        if len(candidates) == 1:
            filenames.append(candidates[0])
        elif len(candidates) > 1:
            print(f"⚠ 占位 __IMAGE_{n}__ 匹配到多个文件：{candidates}")
            sys.exit(1)
        else:
            print(f"⚠ 找不到 __IMAGE_{n}__ 对应的 PNG（目录：{asset_dir}）")
            sys.exit(1)
    return placeholders, filenames


def main():
    args = sys.argv[1:]

    if len(args) >= 2:
        src_html = Path(args[0])
        asset_dir = Path(args[1])
        if len(args) >= 3:
            filenames = [f.strip() for f in args[2].split(",") if f.strip()]
            placeholders = [f"__IMAGE_{i}__" for i in range(1, len(filenames) + 1)]
        else:
            placeholders, filenames = discover_placeholders(src_html, asset_dir)
    elif os.environ.get("WECHAT_VAULT"):
        # 环境变量默认路径（个人复用）
        vault = Path(os.environ["WECHAT_VAULT"])
        src_html = vault / os.environ.get("WECHAT_HTML", "03_草稿/排版.html")
        asset_dir = vault / os.environ.get("WECHAT_ASSETS", "06_素材库")
        imgs = os.environ.get("WECHAT_IMAGES", "")
        if imgs:
            filenames = [f.strip() for f in imgs.split(",") if f.strip()]
            placeholders = [f"__IMAGE_{i}__" for i in range(1, len(filenames) + 1)]
        else:
            placeholders, filenames = discover_placeholders(src_html, asset_dir)
    else:
        print(__doc__)
        print("错误：请传参，或设置 WECHAT_VAULT 环境变量。")
        sys.exit(1)

    if not src_html.exists():
        print(f"✗ 排版 HTML 不存在：{src_html}")
        sys.exit(1)
    if not asset_dir.exists():
        print(f"✗ 图片目录不存在：{asset_dir}")
        sys.exit(1)

    out_html = src_html.with_name(src_html.stem + "_final.html")

    print(f"源 HTML：{src_html}")
    print(f"图片目录：{asset_dir}\n开始上传……\n")

    urls = {}
    for placeholder, fname in zip(placeholders, filenames):
        img_path = asset_dir / fname
        print(f"  ↑ [{placeholder}] 上传 {fname} ...")
        url = upload_via_picgo(img_path)
        urls[placeholder] = url
        print(f"    → {url}\n")

    html = src_html.read_text(encoding="utf-8")
    for ph, url in urls.items():
        if ph in html:
            html = html.replace(ph, url)
        else:
            print(f"⚠ 未找到占位 {ph}（可能已替换过）")

    out_html.write_text(html, encoding="utf-8")
    print(f"✓ 完成！最终文件：{out_html}")
    print("浏览器打开 → Cmd+A → Cmd+C → 粘贴公众号编辑器即可。")


if __name__ == "__main__":
    main()

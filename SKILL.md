---
name: wechat-publish
description: 公众号（WeChat Official Account）文章排版与发布管线。Use when the user wants to (1) 把 Markdown 文章排版成公众号一键复制 HTML, (2) 生成公众号配图（SVG→PNG）, (3) 通过 PicGo 图床上传图片并自动替换占位符, (4) 管理选题/素材/草稿/发布流程。触发场景：公众号排版、公众号配图、一键复制、PicGo、图床、图文排版。
---

# 公众号发布管线（WeChat Publish Pipeline）

把一篇文章从 Markdown 变成「可一键复制到公众号编辑器」的成品，并管理配图与图床上传。

## 何时使用

- 用户要求「公众号排版」「一键复制」「图文排版」
- 用户要求生成配图、封面图
- 用户要求把图片上传图床并替换占位符
- 用户要求管理公众号文章的选题→素材→草稿→发布流程

## 工作流总览

```
Markdown 文章 → ① 排版 HTML（内联 CSS，主题化） → ② 配图 SVG→PNG → ③ PicGo 上传+替换 → ④ 复制发布
```

## 关键约束（务必遵守）

1. **公众号编辑器只认内联样式**：所有 CSS 写进 `style=""` 属性，不用 `<style>` 标签、不用 class、不用 `::before/::after` 伪元素、不用 CSS 渐变（易被过滤）。警示条纹等效果用「色块拼接」实现。
2. **图片必须走 URL**：公众号粘贴 HTML 时只认 `https://` 外链或 `mmbiz.qpic.cn` 图库链接。本地路径（`file://`、相对路径）一律丢失。
3. **图片占位用统一 token**：HTML 里用 `__IMAGE_N__` 作占位符，交给脚本自动替换，避免手动错位。
4. **排版要有独创性，主题必须匹配内容**：不要套用通用「卡片堆叠」模板。按文章的情绪/意象推导视觉主题（调查→档案体、系统→记录仪体、终端→代码体…），见 `references/layout-guide.md` 的「通用方法论」。主色来自意象本身的真实颜色，章节编号方式主题化。
5. **中文渲染验证**：SVG 转 PNG 后，用 headless Chromium 对比渲染差异（差异应 < 5%），或用 OCR 抽查，确保中文不是豆腐块。
6. **文字溢出检测**：手写 SVG 靠肉眼估文字宽度几乎必溢出，必须用工具检测（详见 `references/layout-guide.md`）。

## 目录约定（可自定义）

本 skill 不绑定具体 vault 路径。默认建议结构：

```
<你的内容根目录>/
├── 01_选题库/    选题卡
├── 02_素材收集/  素材卡
├── 03_草稿/      草稿 + 排版 HTML
├── 04_发布记录/  发布记录
├── 06_素材库/    配图（SVG + PNG）
└── 99_模板/      各类卡片模板
```

- 若用 Obsidian，把内容根目录作为 vault；模板放在 `99_模板/`。
- 若用脚本的「环境变量」模式，设置 `WECHAT_VAULT` 指向内容根目录。

## 步骤

### Step 1：撰写/获取文章

- 文章本体存 `03_草稿/`，Markdown，带 YAML frontmatter（title/type/status/tags）。
- 高质量技术文应有底层机制，不止罗列功能。写清「为什么这么设计」。

### Step 2：生成排版 HTML

- 参考 `references/layout-guide.md`：先按「① 通用方法论」从文章内容推导视觉主题，再套对应主题的组件与配色（档案体是案例之一，非唯一）。
- 全内联样式，正文宽 677px，字号 14–15px，行高 1.85–1.9。
- 图片处用 `<img src="__IMAGE_N__" alt="..." style="width:100%;border-radius:6px;display:block;" />`。
- 顶部放 HTML 注释说明使用步骤。

### Step 3：生成配图

- SVG 手绘（黑匣子/档案/记录仪等主题），尺寸 900px 宽。
- 用 `rsvg-convert -w 900 in.svg -o out.png` 转 PNG。
- **⚠️ 必做：文字溢出检测**（详见 `references/layout-guide.md`「SVG 文字溢出检测」）。三步：① 用 macOS Vision OCR 定位每段文字边界框；② 判断 `x+w` 是否超画布/卡片；③ OCR 误报时用 Pillow 像素级复核。长英文词一律「中文大标题 + Menlo 11px 英文小字」，卡片并排先算坐标防重叠。
- 转完用 headless Chromium 截图对比验证中文渲染：
  ```bash
  SHELL=~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell
  "$SHELL" --headless --no-sandbox --disable-gpu --screenshot=/tmp/c.png --window-size=900,H file:///path/to.svg
  ```
  再用 Pillow 对比 rsvg 版与 Chromium 版像素差异（<5% 即正常）。

### Step 4：上传图床 + 替换占位

- 用 `scripts/auto-publish.py`（需 PicGo 已配置图床并开启 Server，默认 `127.0.0.1:36677`）。
- 脚本支持三种调用方式（见脚本 docstring）：显式传参 / 自动推断占位 / 环境变量。
- 脚本自动：上传图片 → 拿 URL → 替换 `__IMAGE_N__` → 输出 `_final.html`。
- 若用户无 PicGo，退化为手动：图片上传公众号素材库拿 `mmbiz.qpic.cn` URL，手动替换占位。

### Step 5：复制发布

- 浏览器打开 `_final.html` → Cmd+A → Cmd+C → 粘贴公众号编辑器。
- 微信会后台自动转存外链图片到其图库。
- 发布后更新 `04_发布记录/` 下的发布记录。

## 触发词速查

公众号排版 / 一键复制 / 图文排版 / 配图 / 封面图 / PicGo / 图床 / 选题卡 / 素材卡

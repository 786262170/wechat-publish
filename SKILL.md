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

## 技能编排（与其他 skill 链式协作）

本 skill 是「编排者」，负责把发布管线串起来，但**具体环节应委托给更擅长的 skill**，不要自己全栈实现。

执行到对应环节时，用 `skill` 工具加载被委托的 skill，遵循其指令完成该环节，再把结果接回本管线。

| 环节 | 委托给 | 触发条件 | 本 skill 负责什么 |
|---|---|---|---|
| 文章创作 | `blog-writer`（个人风格）/ `research-paper-writer`（学术）/ `copywriting`（营销文案） | 需要写/重写文章正文时 | 只做发布，不抢写作的活 |
| 排版 HTML 视觉设计 | `frontend-design` | 设计排版主题、HTML 视觉时 | 提供公众号兼容红线（内联样式等），验收视觉产出 |
| 配图生成（SVG 插图/图表） | **⚠️ 无对口 skill，需检测询问** | 需要生成配图时 | 见下方「配图与裁剪的处理」 |
| 图片裁剪/缩放 | **⚠️ 无对口 skill，可用 ffmpeg/sips 兜底** | 封面裁 2.35:1、裁白边、缩尺寸时 | 见下方「配图与裁剪的处理」 |
| Obsidian vault 管理 | `obsidian-cli` | 读写 vault、验证双链、建选题/素材卡时 | 提供目录约定（01_选题库 等结构） |
| 环境体检 & 图床上传 | **本 skill 自己** | PicGo 检测、上传、占位替换 | 这是本 skill 的独有能力，不外委 |
| SVG 溢出检测 | 本 skill 自己 | 配图完成后 | `references/layout-guide.md` 的方法论 |

### 配图与裁剪的处理（当前无对口 skill）

**配图生成**：`frontend-design` 的定位是「前端界面设计」，**不是**图片/插图生成，别勉强它画 PNG 配图。处理顺序：

1. 先检测是否有对口 skill（如图像生成、插图、图表类），有则委托。
2. 无对口 skill 时，**如实告知用户**「当前没有配图生成 skill」，给两个选择：① 安装对口 skill；② 本 skill 用「手写 SVG」方式兜底生成配图（这是当前已验证可行的做法，见 `references/layout-guide.md`）。

**图片裁剪/缩放**：无对口 skill，用命令行工具兜底，不委托：

- 封面裁 2.35:1、缩尺寸：`ffmpeg`（`ffmpeg-video-editor` 技能的命令可用）或 `sips`（macOS 内置）
- 裁白边：`ffmpeg` 的 crop filter 或 `sips -c`
- 示例：`ffmpeg -i in.png -vf "crop=900:383:0:0" out.png`（裁剪）；`sips -z 383 900 in.png`（缩放到 900×383）



**编排原则**：

1. **先问「有没有更擅长的 skill」，有则委托，无则自己做。** 不要重复造轮子。
2. **委托时不丢上下文**：把本环节的输入（文章主题、目录路径、目标读者）连同委托一起交代清楚。
3. **本 skill 的边界**：发布管线本身——主题推导框架、公众号兼容约束、PicGo 自动化、溢出检测。这四块是本 skill 不可外委的核心，其余尽量委托。
4. **若委托的 skill 缺失，先检测再询问，不要静默退化**：见下方「委托 skill 缺失时的处理流程」。

### 委托 skill 缺失时的处理流程

当需要委托给某个 skill，但不确定它是否已安装时，按以下顺序处理：

1. **检测**：查看当前会话的「可用技能列表」里是否有该 skill 名（如 `blog-writer`、`frontend-design`、`obsidian-cli`）。列表里有 → 直接加载并委托。
2. **确认缺失**：列表里没有 → 用 `ask_user_question` 询问用户是否要安装，说明「缺少 X skill，它擅长什么，装它能带来什么提升」。
3. **用户同意安装**：加载 `find-skills` skill，按其流程搜索并安装（`npx skills add <owner/repo@skill> -g -y`），装好后继续委托。
4. **用户拒绝或安装失败**：才退化为本 skill 自己完成，并在产出里注明「未使用 X skill，效果可能打折」。
5. **绝不静默跳过**：缺失时不要直接自己默默做了，一定要让用户知情并做选择。

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

### Step 0：健康检查（首次使用必做）

- 运行 `python3 scripts/doctor.py`，检查 6 项：PicGo 安装 / Server 监听 / 图床配置 / token 有效 / 仓库可访问 / 存储路径就绪。
- **若 PicGo 已安装但未运行，doctor 会自动启动它**（`open -a PicGo`），并等待后重测 Server。
- 任何一项失败，脚本会输出对应修复指引（安装命令、开启 Server 步骤、生成 token 链接等）。**把指引转述给用户，引导其完成配置后重跑**，直到全绿。
- 存储路径缺失时，可用 `python3 scripts/doctor.py --fix-img` 自动创建（或引导用户手动建目录）。
- 若用户无 PicGo，跳过上传，退化为「图片上传公众号素材库拿 `mmbiz.qpic.cn` URL」手动方案。

### Step 1：撰写/获取文章

- **委托给 `blog-writer` / `research-paper-writer` / `copywriting`**（按文章类型选），除非用户明确只要排版。
- 文章本体存 `03_草稿/`，Markdown，带 YAML frontmatter（title/type/status/tags）。
- 高质量技术文应有底层机制，不止罗列功能。写清「为什么这么设计」。

### Step 2：生成排版 HTML

- **委托给 `frontend-design`** 做 HTML 视觉设计与主题推导（这是它的主场）；本 skill 提供公众号兼容红线（下方「关键约束」）并验收。
- 参考 `references/layout-guide.md`：先按「① 通用方法论」从文章内容推导视觉主题，再套对应主题的组件与配色（档案体是案例之一，非唯一）。
- 全内联样式，正文宽 677px，字号 14–15px，行高 1.85–1.9。
- 图片处用 `<img src="__IMAGE_N__" alt="..." style="width:100%;border-radius:6px;display:block;" />`。
- 顶部放 HTML 注释说明使用步骤。

### Step 3：生成配图

- **配图生成无对口 skill，按「配图与裁剪的处理」执行**：先检测询问是否安装对口 skill，无则用「手写 SVG」兜底（当前已验证可行的做法）。
- 本 skill 负责溢出检测与中文渲染验证（这是本 skill 不可外委的质量把关）。
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

- **先跑 `python3 scripts/doctor.py` 确认环境就绪**（全绿才继续；有失败则按指引引导用户修复）。
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

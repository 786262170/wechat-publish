# wechat-publish

公众号文章「排版 → 配图 → 图床上传 → 一键复制发布」的**编排型技能（Skill）**。

它不自己写文章、不自己画图，而是**把发布管线串起来，并委托给更擅长的 skill**：写作交给 `blog-writer`、视觉交给 `frontend-design`、vault 管理交给 `obsidian-cli`——本 skill 只保留「发布管线」独有的能力：公众号兼容约束、PicGo 自动化、SVG 质量把关。

把一篇 Markdown 文章，变成可直接粘贴到公众号编辑器的成品：内联样式的排版 HTML、无溢出的 SVG 配图、自动上传图床并替换图片占位。

## 特性

- **技能编排**：链式调用 `blog-writer` / `frontend-design` / `obsidian-cli` 等 skill，不重复造轮子
- **排版即叙事**：档案体 / 记录仪体等排版范式，形式服务内容，不套通用卡片模板
- **公众号兼容红线内建**：全内联样式、无 CSS 渐变、无伪元素，规避微信编辑器过滤
- **配图质量保障**：SVG 手绘 + 文字溢出自动检测（Vision OCR + 像素级复核）
- **一键发布**：PicGo 图床自动上传 + 占位符自动替换，生成 `_final.html`
- **环境体检**：doctor.py 首次引导 + 自动启动 PicGo

## 目录结构

```
wechat-publish/
├── SKILL.md                 # 技能指令（触发条件 + 6 步工作流 + 6 条硬约束）
├── scripts/
│   ├── auto-publish.py      # PicGo 上传 + 占位替换（三种调用方式）
│   └── doctor.py            # 健康检查 + 首次使用引导（6 项体检）
├── references/
│   └── layout-guide.md      # 排版设计指南（主题推导方法论 + 多主题案例 + SVG 溢出检测）
└── README.md
```

## 安装

本 skill 是标准 **SKILL.md 目录布局**，可在各主流 agent 工具间移植。核心内容（SKILL.md + scripts + references）100% 通用，只有「安装位置」因工具而异。

### 各 Agent 安装位置一览

| Agent 工具 | skill 目录 | 指令文件（可选） |
|---|---|---|
| DeepSeek Harness（DSH） | `~/.agents/skills/wechat-publish-0.1.0/` | 无需（文件 watcher 自动发现） |
| Claude Code | `~/.claude/skills/wechat-publish/` | `~/.claude/CLAUDE.md` |
| OpenAI Codex | `~/.codex/skills/wechat-publish/` | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/skills/wechat-publish/` | `~/.config/opencode/AGENTS.md` |
| Kimi Code | `~/.kimi-code/skills/wechat-publish/` | `~/.kimi-code/AGENTS.md` |
| GitHub Copilot CLI | `~/.copilot/skills/wechat-publish/` | 无需修改 |
| DeepSeek CLI（非 DSH） | `~/.deepseek/skills/wechat-publish/` | `~/.deepseek/AGENTS.md` |

### 通用安装命令

把本目录复制到对应工具的 skill 根目录即可（以目录名 `wechat-publish` 为例）：

```bash
# Claude Code
mkdir -p ~/.claude/skills && cp -r wechat-publish ~/.claude/skills/

# OpenAI Codex
mkdir -p ~/.codex/skills && cp -r wechat-publish ~/.codex/skills/

# OpenCode
mkdir -p ~/.config/opencode/skills && cp -r wechat-publish ~/.config/opencode/skills/

# Kimi Code
mkdir -p ~/.kimi-code/skills && cp -r wechat-publish ~/.kimi-code/skills/

# DeepSeek Harness（DSH）
mkdir -p ~/.agents/skills && cp -r wechat-publish ~/.agents/skills/wechat-publish-0.1.0
```

### 需要额外激活的工具

部分工具的 skill 目录**不是自动扫描**的，需要在指令文件里加一行引用：

```bash
# Claude Code：追加到 ~/.claude/CLAUDE.md
echo '在发布公众号文章时，加载 wechat-publish skill（~/.claude/skills/wechat-publish/SKILL.md）。' >> ~/.claude/CLAUDE.md

# Codex / OpenCode / Kimi：追加到各自的 AGENTS.md
echo '在发布公众号文章时，加载 wechat-publish skill。' >> ~/.codex/AGENTS.md
echo '在发布公众号文章时，加载 wechat-publish skill。' >> ~/.config/opencode/AGENTS.md
echo '在发布公众号文章时，加载 wechat-publish skill。' >> ~/.kimi-code/AGENTS.md
```

> 说明：DSH 的 `~/.agents/skills/` 由文件系统 watcher 自动发现；Claude Code / Codex / OpenCode 等工具的 skill 目录同样支持目录式安装，只是各工具对「何时加载」的触发方式略有差异（部分需要指令文件里显式引用）。

### 前置依赖

- **PicGo**（图床上传）：`brew install --cask picgo`，配置图床后开启 Server（默认 `127.0.0.1:36677`）
- **rsvg-convert**（SVG→PNG）：`brew install librsvg`
- **headless Chromium**（渲染验证，可选）：Playwright 浏览器即可

## 快速开始

```bash
# 0. 首次使用：健康检查（会引导你配好 PicGo/图床/Server）
python3 scripts/doctor.py

# 1. 准备好排版 HTML（含 __IMAGE_N__ 占位）和配图 PNG
# 2. 显式传参上传
python3 scripts/auto-publish.py 排版.html 图片目录 "img1.png,img2.png,img3.png,img4.png"

# 3. 或自动从 HTML 推断占位符（图片目录按 __IMAGE_N__ 命名）
python3 scripts/auto-publish.py 排版.html 图片目录

# 4. 生成 *_final.html，浏览器打开 → Cmd+A → Cmd+C → 粘贴公众号编辑器
```

`doctor.py` 会检查 6 项（PicGo 安装 / Server 监听 / 图床配置 / token 有效 / 仓库可访问 / 存储路径就绪），任何一项失败都会输出对应的修复指引，是首次使用的最佳入口。

## 许可证

MIT

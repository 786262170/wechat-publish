# wechat-publish

公众号文章「排版 → 配图 → 图床上传 → 一键复制发布」的完整技能（Skill）。

把一篇 Markdown 文章，变成可直接粘贴到公众号编辑器的成品：内联样式的排版 HTML、无溢出的 SVG 配图、自动上传图床并替换图片占位。

## 特性

- **排版即叙事**：档案体 / 记录仪体等排版范式，形式服务内容，不套通用卡片模板
- **公众号兼容红线内建**：全内联样式、无 CSS 渐变、无伪元素，规避微信编辑器过滤
- **配图质量保障**：SVG 手绘 + 文字溢出自动检测（Vision OCR + 像素级复核）
- **一键发布**：PicGo 图床自动上传 + 占位符自动替换，生成 `_final.html`

## 目录结构

```
wechat-publish/
├── SKILL.md                 # 技能指令（触发条件 + 5 步工作流 + 6 条硬约束）
├── scripts/
│   └── auto-publish.py      # PicGo 上传 + 占位替换（三种调用方式）
├── references/
│   └── layout-guide.md      # 排版设计指南（主题推导方法论 + 多主题案例 + SVG 溢出检测）
└── README.md
```

## 安装

### DeepSeek Harness（DSH）

把本目录放到 DSH 的用户 skill 根目录：

```bash
mkdir -p ~/.agents/skills
cp -r wechat-publish ~/.agents/skills/wechat-publish-0.1.0
```

DSH 的文件系统 watcher 会自动发现新 skill（无需重启）。触发词见 SKILL.md 的 description。

### Codex CLI

Codex 不自动扫描 `~/.agents/skills/`，需把 skill 指令合并进 AGENTS.md：

```bash
# 全局 AGENTS.md（或项目级 AGENTS.md）
cat SKILL.md >> ~/.codex/AGENTS.md
```

脚本路径指向 `scripts/auto-publish.py` 即可，脚本是纯 Python 标准库，Codex 的 bash 工具可直接运行。

> 提示：SKILL.md 的「内容」与「脚本」100% 跨 runtime 通用，只有「自动发现」这一层需要按各 runtime 的约定接入（DSH 自动扫描，Codex 走 AGENTS.md，Claude Code 走 `~/.claude/skills/`）。

### 前置依赖

- **PicGo**（图床上传）：`brew install --cask picgo`，配置图床后开启 Server（默认 `127.0.0.1:36677`）
- **rsvg-convert**（SVG→PNG）：`brew install librsvg`
- **headless Chromium**（渲染验证，可选）：Playwright 浏览器即可

## 快速开始

```bash
# 1. 准备好排版 HTML（含 __IMAGE_N__ 占位）和配图 PNG
# 2. 显式传参上传
python3 scripts/auto-publish.py 排版.html 图片目录 "img1.png,img2.png,img3.png,img4.png"

# 3. 或自动从 HTML 推断占位符（图片目录按 __IMAGE_N__ 命名）
python3 scripts/auto-publish.py 排版.html 图片目录

# 4. 生成 *_final.html，浏览器打开 → Cmd+A → Cmd+C → 粘贴公众号编辑器
```

## 许可证

MIT

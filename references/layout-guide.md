# 公众号排版设计指南

本指南分三部分：**① 通用方法论**（怎么选主题、怎么搭组件）、**② 兼容性红线**（所有主题都遵守）、**③ 主题案例**（档案体只是一个示例，可替换）。

核心原则只有一句话：**排版形式服务内容叙事，不要套通用「卡片堆叠」模板。** 每次排版前先问——这篇文章的主题是什么情绪/意象，用什么视觉形式能让读者"读文章 = 进入某种情境"。

---

## ① 通用方法论：从内容推导主题

### 第一步：提取文章的情绪/意象

读文章，回答三个问题：

1. **文章在讲什么「情境」？** 是调查、拆解、复盘、教程、安利、评测，还是观点？
2. **有什么天然的视觉符号？** 文章里反复出现的意象（黑匣子、档案、终端、日记、蓝图、地图…）
3. **读者读完应该有什么感受？** 严谨可信、轻松有趣、硬核专业、复古怀旧……

### 第二步：把意象映射成设计元素

| 意象 → | 主色 | 质感/纹理 | 章节编号方式 | 签名组件 |
|---|---|---|---|---|
| 调查档案 | 牛皮纸 + 印章红 | 纸张横线、打字机 | `EXHIBIT 01` | 结案印章 |
| 飞行记录仪 | 炭黑 + 国际橙 | 警示条纹、雷达波纹 | `REC.01` | 黑匣子箱体 |
| 终端/代码 | 纯黑 + 荧光绿 | 等宽字体、光标 | `$ step 1` | 命令提示符 |
| 蓝图/图纸 | 深蓝底 + 白线 | 网格线、标注箭头 | `DWG-01` | 图框标题栏 |
| 手账/日记 | 米白 + 手写色 | 手绘线、胶带 | `Day 1` | 日期印章 |
| 实验室报告 | 白 + 冷静蓝 | 数据表、刻度 | `EXP-01` | 数据签名 |

规律：**主色来自意象本身的真实颜色**（黑匣子是国际橙、档案是牛皮纸色、蓝图是深蓝），这样配色天然成立、不显刻意。

### 第三步：搭组件骨架

任何主题都绕不开这五类组件，按需组合：

1. **封面卡**：承载标题 + 主题意象（印章/箱体/图框…）
2. **章节头**：主题化的编号方式 + 标题 + 装饰线
3. **强调卡**：金句/结论的视觉落点（深色卡/引用框/盖章）
4. **正文段落**：舒适的排版密度
5. **结尾卡**：收束 + 归档/签名

### 第四步：自检

- [ ] 主题意象是否和文章内容强关联（而不是硬套）
- [ ] 主色是否有"真实来源"（意象本身的颜色）
- [ ] 章节编号方式是否主题化（EXHIBIT/REC/DWG…而非千篇一律"第一章"）
- [ ] 是否避免了通用「白底卡片 + 圆角 + 阴影」的 AI 套路

---

## ② 公众号兼容性红线（所有主题必守）

1. **只用内联 style**，禁 `<style>` 标签、class、伪元素 `::before/::after`
2. **禁 CSS 渐变** `linear-gradient`（微信易过滤）；条纹等效果用「色块 span 拼接」
3. **禁 position:absolute/fixed**；用 float 或 inline-block 布局
4. **字体栈**：`-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif`；等宽用 `Menlo,Consolas,monospace`
5. **正文规格**：宽 677px，字号 14–15px，行高 1.85–1.9，段间距用 section padding
6. **图片占位**：`<img src="__IMAGE_N__" alt="..." style="width:100%;border-radius:6px;display:block;" />`

---

## ③ 主题案例

### 案例 A：调查档案体（NTSB 事故报告）

**适用**：拆解、调查、复盘、溯源类技术文章。

**设计元素**：

- 卷宗封面：案件编号 + 密级章 + 结案印章 + 打字机标题 + 摘要横线
- 章节编号：`EXHIBIT 01` ~ `EXHIBIT 05`
- 牛皮纸档案质感：正文暖色纸底，非纯白
- `FINDINGS` 深色结论卡
- `END OF RECORD` 结尾归档卡

**配色**：

| 用途 | 色值 |
|---|---|
| 牛皮纸底（封面） | `#F0E8D3` |
| 档案纸底（正文） | `#F6F1E3` |
| 墨色文字 | `#2B2620` |
| 正文灰 | `#3A3A36` |
| 印章红 | `#B03A2E` |
| 辅助线 | `#C9BFA4` / `#A89B7D` |

### 案例 B：飞行记录仪体（黑匣子）

**适用**：系统可靠性、监控告警、日志审计类文章。

**设计元素**：炭黑底 + 国际橙 `#FF6B35` + 荧光绿 `#7CFFB2`，警示条纹，`REC.01` 编号，等宽时间戳。

### 案例 C：终端/代码体

**适用**：命令行工具、开发流程、底层原理类文章。

**设计元素**：纯黑底 + 荧光绿，等宽字体为主，`$` 命令提示符做章节头，光标闪烁意象。

> 提示：案例 A 是已实践过的完整方案（含配色表），可直接复用；B、C 是可选方向，用前按「① 通用方法论」补全配色和组件即可。

---

## ④ SVG 文字溢出检测（必做，踩坑沉淀）

手写 SVG 时「用眼睛估文字宽度」几乎必出问题。必须用**工具精确检测**，不能靠肉眼。此节与主题无关，任何配图都适用。

### 三条铁律（避免溢出）

1. **长英文词别做大标题**：等宽/粗体下 19 字符的 `danger-full-access` 20px 会溢出 230px 卡片。长英文词一律放「中文大标题 + 英文小字副标题」，英文用 Menlo 11px 以下。
2. **卡片布局先排坐标再写文字**：多个卡片并排时，先算好每个卡片的 x 范围，确认无重叠再放文字。重叠的经典案例：居中卡片（x=290~510）与并排卡片（x=380~530）在 x 上打架。
3. **文字放容器内留 15px+ 余量**：`text-anchor="middle"` 时，文字半宽不得超过「卡片半宽 - 15px」。

### 检测流程（每次改完 SVG 必跑）

**第一步：OCR 定位**（macOS Vision 框架，识别中文+英文，返回每段文字的边界框 x/y/w）：

```swift
// /tmp/ocr.swift，编译一次可复用
import Vision; import AppKit
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest { r, _ in
  for o in (r.results as? [VNRecognizedTextObservation] ?? []) {
    if let t = o.topCandidates(1).first {
      let bb = o.boundingBox
      print("\(t.string) | x=\(Int(bb.origin.x*1000)) y=\(Int(bb.origin.y*1000)) w=\(Int(bb.size.width*1000))")
    }
  }
}
req.recognitionLanguages = ["zh-Hans", "en-US"]; req.recognitionLevel = .accurate
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
```

编译：`swiftc -module-cache-path /tmp/swift-tmp -o /tmp/ocr /tmp/ocr.swift`
运行：`/tmp/ocr 图.png`

**第二步：判断溢出**。OCR 的 `x + w` 是否 > 画布宽（或 > 卡片右边界）。⚠️ 注意 OCR 边界框对深色背景小字会偏大，OCR 报溢出时需用第三步像素复核。

**第三步：像素级复核**（Pillow，OCR 误报时用）。直接扫文字所在行的实际像素范围：

```python
from PIL import Image
img = Image.open('图.png').convert('RGB')
# 文字是浅灰 #9AA0A8 在深色卡片上：扫 y 行找 130<p<200 的像素最右 x
xs = [x for x in range(600, 900) if 130 < img.getpixel((x, y))[0] < 200]
print(min(xs), max(xs))  # 真实文字范围
```

**结论判定**：像素级的 min/max 才是真相。OCR 只用于快速定位候选问题点。

### 已知坑清单

- `font-weight: bold/900` + `letter-spacing` 会让实际渲染宽度比 Pillow 的 regular 测量宽 20%，布局时按「测量值 × 1.2」留余量。
- 检测「文字是否溢出卡片」时，别把卡片外的画布背景色（浅色）误判成文字像素——先确认卡片真实边界，再扫边界外的文字色。
- 连接线（虚线）穿过卡片间隙是正常设计，不是重叠。

---

## ⑤ 图片规范（通用）

- 配图尺寸：900px 宽（SVG 源 + PNG 双份）
- 封面图：900×383（公众号封面比例 2.35:1）
- 中文渲染验证：SVG→PNG 后必须验证（headless Chromium 对比 + OCR 抽查）

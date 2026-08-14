# 公众号排版设计规范（档案体）

## 设计哲学

排版形式要服务内容叙事，不要套通用「卡片堆叠」模板。让读者"读文章 = 翻一份档案"。

## 本次主题：调查档案体（NTSB 事故报告）

适合「拆解/调查/复盘」类技术文章。核心元素：

- **卷宗封面**：案件编号 + 密级章 + 结案印章 + 打字机标题 + 摘要横线
- **EXHIBIT 编号章节**：每章一个证物编号，替代传统"第一章/第二章"
- **牛皮纸档案质感**：正文用暖色纸底，而非纯白
- **FINDINGS 结论卡**：深色卡片承载最终结论

## 配色（档案体）

| 用途 | 色值 | 说明 |
|---|---|---|
| 牛皮纸底（封面） | `#F0E8D3` | 档案袋色 |
| 档案纸底（正文） | `#F6F1E3` | 略浅，护眼 |
| 墨色文字 | `#2B2620` | 暖黑，非纯黑 |
| 正文灰 | `#3A3A36` | 降低对比，纸质感 |
| 印章红 | `#B03A2E` | 结案章/密级章 |
| 辅助线 | `#C9BFA4` / `#A89B7D` | 档案横线 |

## 公众号兼容性红线（必读）

1. **只用内联 style**，禁 `<style>` 标签、class、伪元素 `::before/::after`
2. **禁 CSS 渐变** `linear-gradient`（微信易过滤）；警示条纹用「色块 span 拼接」
3. **禁 position:absolute/fixed**；用 float 或 inline-block 布局
4. **字体栈**：`-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif`；等宽用 `Menlo,Consolas,monospace`
5. **正文规格**：宽 677px，字号 14–15px，行高 1.85–1.9，段间距用 section padding

## 图片规范

- 占位符：`<img src="__IMAGE_N__" alt="..." style="width:100%;border-radius:6px;display:block;" />`
- 配图尺寸：900px 宽（SVG 源 + PNG 双份）
- 封面图：900×383（公众号封面比例 2.35:1）
- 中文渲染验证：SVG→PNG 后必须验证，见 SKILL.md Step 3

## SVG 文字溢出检测（必做，踩坑沉淀）

手写 SVG 时「用眼睛估文字宽度」几乎必出问题。必须用**工具精确检测**，不能靠肉眼。

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

## 组件清单（档案体）

1. 卷宗封面卡（案件号 + 密级章 + 标题 + 结案印章 + 归档条）
2. INVESTIGATION OPENING 引言框（白底 + 左红边）
3. EXHIBIT 章节头（深色编号标签 + 标题 + 红短线）
4. 正文段落 + 圆点列表
5. 配图 `<img>` 占位
6. FINDINGS 深色结论卡
7. END OF RECORD 结尾归档卡

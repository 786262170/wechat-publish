# 成品例文库（Examples Library）

每次完成一篇公众号排版后，把成品归档到这里，让 skill「越用越强」。

## 样例目录结构

每个样例是一个目录，命名 `YYYY-MM-DD-slug/`：

```
examples/
├── 2026-08-14-dsh-archives/    # 样例：调查档案体
│   ├── 排版.html                 # 最终排版（含图片 URL，可直接复制发布）
│   ├── meta.md                   # 说明：文章类型/视觉主题/可复用元素/踩坑
│   └── assets/                   # （可选）配图 PNG
└── ...
```

## 归档时机

每次 Step 6（见 SKILL.md）确认成品 final 后，执行 `scripts/manage-examples.py add` 或手动归档。

## meta.md 必填字段

- 日期、文章类型、视觉主题
- 可复用元素（组件/配色/章节编号方式）
- 配图清单
- 踩坑记录（这次新学到的经验，回写给 layout-guide）

## 库容量管理

- 上限 20 个样例
- 超限时用 `python3 scripts/manage-examples.py` 查看，`prune` 修剪最旧的 5 个
- 修剪前需用户确认

## 使用方式

排版新文章前，先扫一眼例文库，找「同类文章类型」的样例作参考，避免从零开始。

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成品例文库管理脚本

用法：
  python3 manage-examples.py             # 查看库状态（样例数 + 清单）
  python3 manage-examples.py prune       # dry-run 修剪最旧的 5 个（预览）
  python3 manage-examples.py prune --execute  # 实际修剪
  python3 manage-examples.py add <目录>  # 归档一个新样例（复制目录进 examples/）

约定：
  - 每个样例是一个目录，命名 YYYY-MM-DD-slug/
  - 目录内至少含 排版.html 和 meta.md
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "references" / "examples"
MAX_EXAMPLES = 20
PRUNE_COUNT = 5


def list_examples():
    """列出所有样例目录，按日期排序（旧在前）。"""
    examples = []
    for d in EXAMPLES_DIR.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        try:
            date = datetime.strptime(d.name[:10], "%Y-%m-%d")
            examples.append((date, d.name))
        except ValueError:
            continue
    return sorted(examples, key=lambda x: x[0])


def check_library():
    examples = list_examples()
    count = len(examples)
    print("=" * 48)
    print("成品例文库状态")
    print("=" * 48)
    print(f"样例总数：{count}")
    print(f"上限：{MAX_EXAMPLES}")
    print()
    if count > MAX_EXAMPLES:
        print(f"⚠️  超出上限 {count - MAX_EXAMPLES} 个，建议修剪最旧的 {PRUNE_COUNT} 个：")
        for i, (date, name) in enumerate(examples[:PRUNE_COUNT], 1):
            print(f"  {i}. {name}（{date.strftime('%Y-%m-%d')}）")
    else:
        print(f"✓ 在限额内（还可存 {MAX_EXAMPLES - count} 个）")
    print()
    print("全部样例（旧在前）：")
    print("-" * 48)
    for date, name in examples:
        print(f"  {date.strftime('%Y-%m-%d')}  {name}")


def prune(dry_run=True):
    examples = list_examples()
    if len(examples) <= MAX_EXAMPLES:
        print("库在限额内，无需修剪。")
        return
    to_remove = examples[:PRUNE_COUNT]
    verb = "将删除" if not dry_run else "DRY RUN 将删除"
    print(f"{verb} {len(to_remove)} 个最旧样例：")
    for date, name in to_remove:
        d = EXAMPLES_DIR / name
        if not dry_run:
            shutil.rmtree(d)
        print(f"  {'已删除' if not dry_run else '  将删'}: {name}")


def add(src_dir):
    src = Path(src_dir)
    if not src.is_dir():
        print(f"✗ 源目录不存在：{src}")
        sys.exit(1)
    if not (src / "排版.html").exists() and not (src / "meta.md").exists():
        print("✗ 样例目录需含 排版.html 或 meta.md")
        sys.exit(1)
    dst = EXAMPLES_DIR / src.name
    if dst.exists():
        print(f"✗ 目标已存在：{dst}（请先删除或改名）")
        sys.exit(1)
    shutil.copytree(src, dst)
    print(f"✓ 已归档样例：{dst.relative_to(EXAMPLES_DIR.parent)}")


def main():
    args = sys.argv[1:]
    if not args:
        check_library()
    elif args[0] == "prune":
        prune(dry_run="--execute" not in args)
    elif args[0] == "add" and len(args) == 2:
        add(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

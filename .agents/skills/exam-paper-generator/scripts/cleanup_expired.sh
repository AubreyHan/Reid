#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)/试卷"

python3 - "$DEFAULT_ROOT" "$@" <<'PY'
import argparse
import os
import shutil
import sys
import time
from pathlib import Path


def latest_mtime(path: Path) -> float:
    """Return the most recent mtime of a file, or of a directory and all files inside it."""
    if path.is_file() or path.is_symlink():
        return path.stat().st_mtime
    newest = path.stat().st_mtime
    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        for name in files:
            if name == ".DS_Store":
                continue
            try:
                mt = (root_path / name).stat().st_mtime
                if mt > newest:
                    newest = mt
            except FileNotFoundError:
                pass
    return newest


def main() -> int:
    default_root = sys.argv[1]
    parser = argparse.ArgumentParser(
        description="自动清理 试卷/<科目>/ 下超过指定天数的过期试卷文件及独立试卷目录。"
    )
    parser.add_argument(
        "--root",
        default=default_root,
        help="试卷根目录路径（默认：<项目根目录>/试卷）",
    )
    parser.add_argument(
        "--days",
        type=float,
        default=10.0,
        help="保留天数，超过该天数的试卷将被删除（默认：10）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览将被删除的过期试卷，不实际执行删除",
    )
    args = parser.parse_args(sys.argv[2:])

    exams_root = Path(args.root).resolve()
    if not exams_root.is_dir():
        print(f"试卷目录不存在，跳过清理：{exams_root}")
        return 0
    if exams_root.name != "试卷":
        print(f"Error: 为安全起见，目标目录名必须为 '试卷'，当前为：{exams_root}", file=sys.stderr)
        return 1

    cutoff = time.time() - args.days * 86400
    expired: list[tuple[Path, float]] = []

    for subject_dir in sorted(exams_root.iterdir()):
        if not subject_dir.is_dir() or subject_dir.name.startswith("."):
            continue
        for entry in sorted(subject_dir.iterdir()):
            if entry.name.startswith("."):
                continue
            mt = latest_mtime(entry)
            if mt < cutoff:
                expired.append((entry, (time.time() - mt) / 86400))

    if not expired:
        print(f"未发现超过 {args.days:g} 天的过期试卷。")
        return 0

    action = "计划删除（dry-run）" if args.dry_run else "已删除"
    for entry, age_days in expired:
        rel = entry.relative_to(exams_root.parent)
        kind = "目录" if entry.is_dir() else "文件"
        if not args.dry_run:
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        print(f"{action} [{kind}] {rel}（已存放 {age_days:.1f} 天）")

    print(f"共{action} {len(expired)} 项过期试卷。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

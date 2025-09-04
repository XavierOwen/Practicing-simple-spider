#!/usr/bin/env python3
import argparse, pathlib, re, shutil, sys

# 1) 只替换 U+2500 为 “——”（两枚 EM DASH）
REPLACE_MAP = {
    "\u2500": "——",  # BOX DRAWINGS LIGHT HORIZONTAL → EM DASH × 2
    "——声": "",
    "﹃":"『",
    "﹄":"』"
}

# 2) 需要“删除”的集合
# - C0 控制字符（保留 \n \r \t）与 DEL
CTRL_PATTERN = r"[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]"
# - 私用区 PUA（含 U+E216 等）
PUA_PATTERN  = r"[\uE000-\uF8FF]"
# - 几何图形块（含 U+25A1 等各类方块符号）
GEOM_PATTERN = r"[\u25A0-\u25FF]"

DELETE_RE = re.compile(f"(?:{CTRL_PATTERN}|{PUA_PATTERN}|{GEOM_PATTERN})")

def clean_text(s: str) -> str:
    # 先做精确替换（避免把 \u2500 当作几何图形误删）
    for src, dst in REPLACE_MAP.items():
        s = s.replace(src, dst)
    # 再删除“方块类 / 私用区 / 控制符”
    s = DELETE_RE.sub("", s)
    return s

def main():
    ap = argparse.ArgumentParser(description="Clean Markdown: replace U+2500 with '——' and remove squares/PUA/control chars")
    ap.add_argument("input", help="input .md file")
    ap.add_argument("-o", "--output", help="output file (default: stdout unless --inplace)")
    ap.add_argument("--inplace", action="store_true", help="overwrite input (creates .bak)")
    args = ap.parse_args()

    src = pathlib.Path(args.input)
    if not src.exists():
        print(f"File not found: {src}", file=sys.stderr); sys.exit(1)

    text = src.read_text(encoding="utf-8", errors="strict")
    cleaned = clean_text(text)

    if args.inplace:
        bak = src.with_suffix(src.suffix + ".bak")
        shutil.copyfile(src, bak)
        src.write_text(cleaned, encoding="utf-8")
        print(f"Done. In-place cleaned: {src.name} (backup: {bak.name})")
    elif args.output:
        out = pathlib.Path(args.output)
        out.write_text(cleaned, encoding="utf-8")
        print(f"Done. Wrote: {out}")
    else:
        sys.stdout.write(cleaned)

if __name__ == "__main__":
    main()
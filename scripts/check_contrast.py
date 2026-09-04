#!/usr/bin/env python3
"""
check_contrast.py — 테마별 색 조합의 대비비를 검사합니다. (WCAG 2.1 AA)

테마를 새로 만들 때 가장 자주 나는 사고가 "브랜드색 위 흰 텍스트가 안 읽힘"입니다.
고객사 테마를 추가할 때마다 이 스크립트를 돌리면 그 사고가 배포 전에 잡힙니다.

기준: 본문 4.5:1 / 큰 텍스트(18px 이상 굵게) 3:1 / UI 경계 3:1
사용:  python3 scripts/check_contrast.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))

# (전경, 배경, 최소비, 설명)
PAIRS = [
    ("text.primary",   "surface.default", 4.5, "본문 텍스트"),
    ("text.secondary", "surface.default", 4.5, "보조 텍스트"),
    ("text.tertiary",  "surface.default", 4.5, "플레이스홀더"),
    ("text.brand",     "surface.default", 4.5, "브랜드 텍스트·고스트 버튼"),
    ("text.inverse",   "brand.primary",   4.5, "주요 버튼 라벨"),
    ("text.inverse",   "danger.default",  4.5, "위험 버튼 라벨"),
    ("text.inverse",   "surface.inverse", 4.5, "토스트 라벨"),
    ("brand.onSubtle", "brand.subtle",    4.5, "선택된 칩"),
    ("danger.text",    "danger.subtle",   4.5, "에러 토스트·헬퍼"),
    ("success.default", "success.subtle", 4.5, "성공 뱃지"),
    ("warning.default", "warning.subtle", 4.5, "경고 뱃지"),
    ("border.default", "surface.default", 3.0, "입력 필드 경계"),
    ("brand.primary",  "surface.default", 3.0, "포커스 링·인디케이터"),
]


def parse_css_vars(theme):
    css = (ROOT / "docs" / "tokens" / f"eluon-{theme}.css").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip()
            for m in re.finditer(r"--color-([a-zA-Z0-9-]+):\s*([^;]+);", css)}


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = luminance(hex_to_rgb(fg)), luminance(hex_to_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    failed = 0
    for theme in CONFIG["themes"]:
        vars_ = parse_css_vars(theme)
        print(f"\n[{theme}]")
        for fg, bg, minimum, label in PAIRS:
            fk, bk = fg.replace(".", "-"), bg.replace(".", "-")
            if fk not in vars_ or bk not in vars_:
                print(f"  ? {label}: 토큰 없음 ({fg} / {bg})")
                continue
            r = ratio(vars_[fk], vars_[bk])
            ok = r >= minimum
            failed += 0 if ok else 1
            mark = "✓" if ok else "✗"
            print(f"  {mark} {label:<22} {r:5.2f}:1  (기준 {minimum}) "
                  f"{fg} on {bg}")
    if failed:
        print(f"\n{failed}건이 기준 미달입니다. 테마 토큰을 조정하세요.")
        return 1
    print("\n모든 조합이 기준을 만족합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

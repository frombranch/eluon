#!/usr/bin/env python3
"""
build_tokens.py — 토큰 JSON을 CSS 변수로 펼칩니다.

core.json 하나에 테마 오버라이드를 얹어 테마별 CSS를 만듭니다.
컴포넌트는 이 CSS 변수만 참조하므로, 테마 교체가 컴포넌트를 건드리지 않습니다.

산출: docs/tokens/eluon-<theme>.css  (문서 사이트와 렌더러가 함께 씁니다)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKENS = ROOT / "tokens"

REF = re.compile(r"^\{primitive\.([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\}$")


def deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load(theme):
    core = json.loads((TOKENS / "core.json").read_text(encoding="utf-8"))
    if theme == "core":
        return core
    path = TOKENS / f"theme-{theme}.json"
    if not path.exists():
        raise SystemExit(f"테마 파일이 없습니다: {path.name}")
    return deep_merge(core, json.loads(path.read_text(encoding="utf-8")))


def resolve(value, prim):
    """{primitive.blue.500} 참조를 실제 값으로 바꿉니다."""
    m = REF.match(value) if isinstance(value, str) else None
    if not m:
        return value
    family, step = m.groups()
    try:
        return prim[family][step]
    except KeyError:
        raise SystemExit(f"토큰 참조를 찾을 수 없습니다: {value}")


def to_css(tokens, theme):
    prim = tokens["primitive"]
    sem = tokens["semantic"]
    lines = [f"/* Eluon tokens — theme: {theme}. build_tokens.py가 생성합니다. 직접 고치지 마세요. */",
             ":root{"]

    for family, steps in prim.items():
        for step, val in steps.items():
            lines.append(f"  --p-{family}-{step}:{val};")

    for key, val in sem["color"].items():
        lines.append(f"  --color-{key.replace('.', '-')}:{resolve(val, prim)};")
    for key, val in sem["font"].items():
        lines.append(f"  --font-{key.replace('.', '-')}:{val};")
    for key, val in sem.get("size", {}).items():
        lines.append(f"  --size-{key.replace('.', '-')}:{val}px;")
    for key, val in sem.get("breakpoint", {}).items():
        lines.append(f"  --bp-{key}:{val}px;")
    for key, val in sem["radius"].items():
        lines.append(f"  --radius-{key}:{val}px;")
    for key, val in sem["space"].items():
        lines.append(f"  --space-{key}:{val}px;")
    for key, val in sem["elevation"].items():
        lines.append(f"  --elevation-{key}:{val};")
    # 레이아웃. 열 개수는 단위가 없고, 본문 길이는 ch 입니다.
    # 한글 조판. 값이 CSS 키워드라 단위를 붙이지 않습니다.
    for key, val in sem.get("text", {}).items():
        lines.append(f"  --text-{key}:{val};")
    for key, val in sem.get("layout", {}).items():
        unit = "" if key == "grid.columns" else ("ch" if key == "text.measure" else "px")
        lines.append(f"  --layout-{key.replace('.', '-')}:{val}{unit};")

    for name, d in tokens["typography"].items():
        safe = name.replace(".", "-")
        lines.append(f"  --type-{safe}-size:{d['size']}px;")
        lines.append(f"  --type-{safe}-weight:{d['weight']};")
        lines.append(f"  --type-{safe}-lh:{d['lineHeight']};")
        lines.append(f"  --type-{safe}-tracking:{d['tracking']};")
        # 한 줄로 쓰는 축약형. 매번 네 줄 쓰다 빠뜨리는 걸 막습니다.
        lines.append(f"  --type-{safe}:{d['weight']} {d['size']}px/{d['lineHeight']} "
                     f"var(--font-family-base);")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    config = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
    themes = config["themes"]
    out_dir = ROOT / "docs" / "tokens"
    out_dir.mkdir(parents=True, exist_ok=True)
    for theme in themes:
        tokens = load(theme)
        (out_dir / f"eluon-{theme}.css").write_text(to_css(tokens, theme), encoding="utf-8")
        print(f"✓ docs/tokens/eluon-{theme}.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())

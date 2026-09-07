#!/usr/bin/env python3
"""
render.py — 레시피를 @2x PNG로 렌더하고 사이드카 JSON을 함께 씁니다.

핵심: spec 수치가 CSS에 그대로 들어가고 그 CSS가 그대로 렌더됩니다.
그래서 manifest의 spec과 실제 이미지가 어긋날 수 없습니다.

사용:
    python3 scripts/render.py                  # 전체 테마
    python3 scripts/render.py --theme eluo     # 특정 테마만
    python3 scripts/render.py --only btn       # ID 접두 필터
"""
import argparse
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from recipes.components import BASE_CSS, build  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
THEMES = CONFIG["themes"]
SITES = CONFIG.get("sites", {})


def themes_for(pack):
    """이 pack 을 드는 테마들. core 는 전부. CLAUDE.md §D."""
    if pack == "core":
        return list(THEMES)
    return [t for t in THEMES if pack in (SITES.get(t, {}).get("packs") or [])]

GROUP_DIR = {
    "button": "button", "chip": "chip", "input": "input", "card": "card",
    "navigation": "navigation", "table": "table", "feedback": "feedback",
    "badge": "badge", "modal": "modal", "commerce": "commerce", "layout": "layout",
    "disclosure": "disclosure", "booking": "booking",
}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<style>
@font-face{{font-family:Pretendard;src:local('Pretendard');font-weight:100 900}}
{tokens}
{base}
{css}
html,body{{background:transparent}}
body{{display:inline-block;padding:0}}
</style></head><body><div class="stage" id="shot">{html}</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=THEMES)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("playwright가 필요합니다: pip install playwright --break-system-packages")

    themes = [args.theme] if args.theme else THEMES
    core_tokens = json.loads((ROOT / "tokens" / "core.json").read_text(encoding="utf-8"))
    comps = [c for c in build(core_tokens) if c["id"].startswith(args.only)]
    if not comps:
        raise SystemExit("렌더할 컴포넌트가 없습니다.")

    made = 0
    wrote_sidecar = set()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for theme in themes:
            css_path = ROOT / "docs" / "tokens" / f"eluon-{theme}.css"
            if not css_path.exists():
                raise SystemExit("먼저 build_tokens.py 를 실행하세요.")
            token_css = css_path.read_text(encoding="utf-8")
            page = browser.new_page(device_scale_factor=2)

            for c in comps:
                # 그 pack 을 안 드는 테마는 이 자산을 렌더하지 않습니다.
                if theme not in themes_for(c.get("pack", "core")):
                    continue
                page.set_content(PAGE.format(tokens=token_css, base=BASE_CSS,
                                             css=c["css"], html=c["html"]))
                page.wait_for_timeout(60)
                folder = ROOT / "assets" / "components" / GROUP_DIR[c["group"]]
                folder.mkdir(parents=True, exist_ok=True)
                rel = f"assets/components/{GROUP_DIR[c['group']]}/{c['id']}--{theme}@2x.png"
                page.locator("#shot").screenshot(path=str(ROOT / rel), omit_background=True)
                made += 1

                # 사이드카는 이 자산을 처음 렌더할 때 한 번만 씁니다.
                # "첫 테마" 로 못박으면, 그 테마가 이 자산의 pack 을 안 들 때
                # 사이드카가 영영 안 써집니다(FAILURES.md#sidecar-first-theme).
                if c["id"] not in wrote_sidecar:
                    wrote_sidecar.add(c["id"])
                    sidecar = {
                        "id": c["id"], "name": c["name"], "group": c["group"],
                        "tags": c.get("tags", []),
                        "spec": c["spec"], "tokens": c.get("tokens", {}),
                        "responsive": c.get("responsive", {}),
                        "states": c.get("states", []),
                        "usage": c["usage"], "dont": c.get("dont", ""),
                        "status": c.get("status", "stable"), "since": c.get("since", "v1.0.0"),
                        "pack": c.get("pack", "core"),
                        # 상태 변형은 부모에 매답니다. 없으면 키 자체를 넣지 않습니다.
                        **({"variantOf": c["variantOf"],
                            "variantState": c["variantState"]} if c.get("variantOf") else {}),
                        "renders": {t: f"assets/components/{GROUP_DIR[c['group']]}/"
                                       f"{c['id']}--{t}@2x.png"
                                    for t in themes_for(c.get("pack", "core"))},
                    }
                    (folder / f"{c['id']}.json").write_text(
                        json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
            page.close()
        browser.close()

    print(f"✓ 렌더 {made}장 · 컴포넌트 {len(comps)}개 · 테마 {len(themes)}종")
    return 0


if __name__ == "__main__":
    sys.exit(main())

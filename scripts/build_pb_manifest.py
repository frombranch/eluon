#!/usr/bin/env python3
"""
build_pb_manifest.py — manifest.json 을 프롬프트 빌더가 읽는 형식(eluon.json)으로 옮깁니다.

빌더(eluon-prompt-builder)는 자체 스키마를 요구합니다. manifest.json 과 다른 점은 넷입니다.
    schema: 1        manifest 에는 없음
    source.*         manifest 에는 repo·docs·tokens 가 최상위에 흩어져 있음
    groups[]         manifest 에는 없음 (각 자산의 group 문자열로만 존재)
    spec             manifest 는 객체, 빌더는 사람이 읽는 한 줄 문자열

manifest.json 을 고치지 않고 이 스크립트가 변환본을 따로 만듭니다.
산출: docs/eluon.json  (docs/prompt-builder.html 이 같은 폴더에서 읽습니다)
eluon.json 도 생성물입니다. 손으로 고치지 마세요.

사용:
    python3 scripts/build_pb_manifest.py
    python3 scripts/build_pb_manifest.py --check   # 커밋본이 낡았으면 실패 (CI용)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
CHECK_ONLY = "--check" in sys.argv

# build_docs.py 의 GROUP_KO 와 같은 표입니다.
# 새 그룹이 생기면 여기에도 넣어야 합니다 — 빠뜨리면 아래 build() 가 실패시킵니다.
GROUP_KO = {
    "button": "버튼", "chip": "칩", "input": "입력", "card": "카드",
    "navigation": "내비게이션", "table": "테이블", "feedback": "피드백",
    "badge": "뱃지", "modal": "모달", "commerce": "커머스", "layout": "레이아웃",
    "disclosure": "접기",
}

# 빌더의 테마 선택 버튼에 그대로 나갑니다. CLAUDE.md 2절의 설명을 따릅니다.
# 빌더 화면에 그대로 보이는 문장입니다. 헥스코드나 전문 용어를 쓰지 않습니다.
# 이름은 전부 가명이므로 어느 고객사인지는 여기에 적지 않습니다.
THEME_KO = {
    "core": ("중립 코어", "브랜드를 아직 안 정했을 때 쓰는 무채색"),
    "eluo": ("ELUO", "우리 회사 기본값. 자사 제안서와 내부 산출물에 씁니다"),
    "atlas": ("아틀라스", "고객사 테마. 진한 남색에 산호색 포인트"),
    "ember": ("엠버", "고객사 테마. 진한 초록. 이름과 색이 다르니 주의하세요"),
    "harbor": ("하버", "고객사 테마. 따뜻한 갈색. 고객사 웹사이트에서 값을 가져왔습니다"),
    "tideland": ("타이드랜드", "고객사 테마. 주황빛. 색까지 추정이라 대외 제출물에 쓰지 마세요"),
    "cobalt": ("코발트", "고객사 테마. 진한 남색에 파랑 포인트. 버튼이 전부 알약 테두리형입니다"),
}

# 크기 토큰의 앞머리(control.lg.height → control)를 사람 말로. 프롬프트의 경고 문장에 씁니다.
SIZE_GROUP_KO = {
    "control": "버튼", "chip": "칩", "badge": "배지", "card": "카드",
    "field": "입력 필드", "table": "테이블", "tab": "탭", "toast": "토스트",
    "modal": "모달", "pagination": "페이지네이션", "toggle": "토글",
    "section": "섹션 헤더", "price": "가격", "border": "테두리 두께",
    "focusRing": "포커스 링", "icon": "아이콘",
    # v1.8.0 페이지 블록 · v1.10.0 보조 어휘
    "header": "헤더", "hero": "히어로", "footer": "푸터", "ctaBand": "CTA 띠",
    "listRow": "목록 행", "accordion": "아코디언", "breadcrumb": "경로",
    "empty": "빈 상태", "descList": "정의 목록", "stepFlow": "절차",
}

# spec 한 줄로 펼칠 때의 순서. 여기 없는 키는 manifest 에 적힌 순서 그대로 뒤에 붙습니다.
SPEC_ORDER = [
    "width", "height", "radius", "paddingX", "paddingY",
    "gap", "borderWidth", "elevation", "typography",
]


def spec_line(spec: dict) -> str:
    """{"height":56,"radius":"lg"} → "height 56 · radius lg". 값은 손대지 않습니다."""
    keys = [k for k in SPEC_ORDER if k in spec]
    keys += [k for k in spec if k not in keys]
    return " · ".join(f"{k} {spec[k]}" for k in keys)


def size_status(theme: str, all_groups: set):
    """이 테마가 실제로 덮어쓴 크기 축과, core 기본값을 그대로 쓰는 축을 갈라 냅니다.

    기본 테마(자사)는 core 값이 곧 정답이라 판정 대상이 아닙니다.
    고객사 테마는 안 덮어쓴 축이 곧 '아직 안 잰 축'입니다."""
    if theme == CONFIG["defaultTheme"]:
        return None
    path = ROOT / "tokens" / f"theme-{theme}.json"
    if not path.exists():
        return None
    over = json.loads(path.read_text(encoding="utf-8")).get("semantic", {}).get("size") or {}
    got = {k.split(".")[0] for k in over}
    ko = lambda g: SIZE_GROUP_KO.get(g, g)
    return {
        "sizeMeasured": sorted({ko(g) for g in got}),
        "sizeInherited": sorted({ko(g) for g in all_groups - got}),
    }


def foundation_status(theme: str, core: dict):
    """레이아웃·활자를 이 테마가 실제로 덮어썼는지. 크기와 같은 판정입니다.
    안 덮어썼으면 우리 기본값이고, 고객사 산출물에는 그렇다고 밝혀야 합니다."""
    if theme == CONFIG["defaultTheme"]:
        return None
    path = ROOT / "tokens" / f"theme-{theme}.json"
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    lay = (d.get("semantic") or {}).get("layout") or {}
    fam = ((d.get("semantic") or {}).get("font") or {})
    typ = d.get("typography") or {}
    return {
        "layoutMeasured": bool(lay),
        "typeMeasured": bool(typ),
        "fontMeasured": bool(fam),
    }


def fnd_lines(f: dict) -> dict:
    """빌더가 프롬프트에 그대로 실을 수 있게 한 줄씩 만들어 둡니다."""
    lay = f.get("layout", {})
    typ = f.get("typography", {})
    return {
        "layout": [f"{k} {v}" for k, v in lay.items()],
        "type": [f"{k} — {v.get('role','')} {v['size']}/{v['weight']}/"
                 f"{v['lineHeight']}/{v['tracking']}" for k, v in typ.items()],
        "fontBase": f.get("font", {}).get("family.base", ""),
        "text": f.get("text", {}),
    }


def build(manifest: dict):
    errors = []

    assets, dropped = [], []
    for a in manifest["assets"]:
        if a.get("status") == "deprecated":
            # CLAUDE.md 6항 — deprecated 는 쓰지 않습니다. 고를 수 없게 아예 빼둡니다.
            dropped.append(a["id"])
            continue
        if a.get("variantOf"):
            # 상태는 고르는 물건이 아닙니다. 부모에 붙여 함께 나갑니다.
            continue
        assets.append({
            "id": a["id"],
            "name": a.get("name", a["id"]),
            "group": a["group"],
            "spec": spec_line(a.get("specByTheme", {}).get(
                CONFIG["defaultTheme"], a["spec"])),
            # 치수는 테마마다 다릅니다. 빌더가 고른 테마의 수치를 프롬프트에 실어야
            # 시안이 그 고객사 규격으로 나옵니다. (D-029)
            "specByTheme": {th: spec_line(sp)
                            for th, sp in a.get("specByTheme", {}).items()},
            "usage": a.get("usage", ""),
            "dont": a.get("dont", ""),
            "tags": a.get("tags", []),
            "responsiveByTheme": {th: {str(px): how for px, how in (r or {}).items()}
                                  for th, r in (a.get("responsiveByTheme") or {}).items()},
            "states": a.get("states", []),
            # 상태마다 무엇이 달라지는지. 프롬프트가 "에러면 테두리를 danger 로" 를
            # 말할 수 있어야 합니다.
            "variants": [{"id": v["id"], "state": v["state"],
                          "tokens": v.get("tokens", {})}
                         for v in a.get("variants", [])],
        })

    used = {a["group"] for a in assets}
    unknown = sorted(used - set(GROUP_KO))
    if unknown:
        errors.append("GROUP_KO 에 없는 그룹: " + ", ".join(unknown) + " — 이 표에 한글 이름을 추가하세요")

    missing_theme = [t for t in CONFIG["themes"] if t not in THEME_KO]
    if missing_theme:
        errors.append("THEME_KO 에 없는 테마: " + ", ".join(missing_theme))

    if errors:
        return None, errors, dropped

    groups = [{"id": g, "label": GROUP_KO[g]} for g in GROUP_KO if g in used]

    core_size = json.loads((ROOT / "tokens" / "core.json").read_text(encoding="utf-8"))
    all_groups = {k.split(".")[0] for k in core_size["semantic"].get("size", {})}
    themes = []
    for t in CONFIG["themes"]:
        th = {"id": t, "label": THEME_KO[t][0], "hint": THEME_KO[t][1]}
        st = size_status(t, all_groups)
        if st:
            th.update(st)
        fs = foundation_status(t, core_size)
        if fs:
            th.update(fs)
        th["status"] = manifest.get("themeStatus", {}).get(t, "measured")
        th["foundation"] = fnd_lines(manifest["foundationByTheme"][t])
        themes.append(th)

    out = {
        "schema": 1,
        "source": {
            "name": manifest["name"],
            "repo": manifest["repo"],
            "tag": manifest["version"],
            # 빌더는 이 값을 프롬프트의 <link> 주소로 그대로 씁니다.
            # 저장소 상대경로를 넣으면 링크가 깨지므로 CDN URL 을 넣습니다.
            "tokensPath": manifest["tokens"][CONFIG["defaultTheme"]]
                .replace(f"eluon-{CONFIG['defaultTheme']}.css", "eluon-{theme}.css"),
            "docsSite": manifest["docs"],
            "manifestPath": "manifest.json",
            "docsPath": "CLAUDE.md",
        },
        "themes": themes,
        "groups": groups,
        "assets": assets,
    }
    return out, [], dropped


def verify(m: dict):
    """빌더의 validate() 와 같은 검사를 여기서 미리 돌립니다.
    빌더에서 튕기는 파일을 커밋하지 않기 위한 것입니다."""
    e = []
    if m.get("schema") != 1:
        e.append("schema 가 1이 아님")
    if not m.get("source", {}).get("repo"):
        e.append("source.repo 없음")
    for key in ("themes", "groups", "assets"):
        if not isinstance(m.get(key), list) or not m[key]:
            e.append(f"{key} 가 비어 있음")
    # 빌더의 validate() 는 원소 모양을 안 봅니다. 통과하고도 화면이 깨지므로 여기서 잡습니다.
    for t in m.get("themes", []):
        if not isinstance(t, dict) or not t.get("id"):
            e.append(f"themes 원소에 id 가 없음: {t!r}")
    for g in m.get("groups", []):
        if not isinstance(g, dict) or not g.get("id"):
            e.append(f"groups 원소에 id 가 없음: {g!r}")
    gids = {g["id"] for g in m.get("groups", []) if isinstance(g, dict)}
    for a in m.get("assets", []):
        if not a.get("id") or not a.get("spec"):
            e.append(f"자산에 id 또는 spec 이 없음: {a.get('id', '(id 없음)')}")
        if not isinstance(a.get("spec"), str):
            e.append(f"{a.get('id')}: spec 이 문자열이 아님 — 빌더가 [object Object] 로 출력합니다")
        for th, s in (a.get("specByTheme") or {}).items():
            if not isinstance(s, str):
                e.append(f"{a.get('id')}: specByTheme.{th} 가 문자열이 아님")
        if a.get("group") not in gids:
            e.append(f"{a.get('id')}: groups 에 없는 그룹 '{a.get('group')}'")
        if not a.get("usage"):
            e.append(f"{a.get('id')}: usage 가 비어 있음 — Claude 가 고를 근거가 없습니다")
    return e


def main() -> int:
    mf = ROOT / "manifest.json"
    if not mf.exists():
        print("manifest.json 이 없습니다. 먼저 build_manifest.py 를 돌리세요.")
        return 1
    manifest = json.loads(mf.read_text(encoding="utf-8"))

    out, errors, dropped = build(manifest)
    if errors:
        print("빌드 실패:\n" + "\n".join(f"  ✗ {e}" for e in errors))
        return 1

    problems = verify(out)
    if problems:
        print("빌더가 읽지 못하는 결과입니다:\n" + "\n".join(f"  ✗ {p}" for p in problems))
        return 1

    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    target = ROOT / "docs" / "eluon.json"

    if CHECK_ONLY:
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            print("커밋본이 낡았습니다. build_pb_manifest.py 를 다시 돌리세요: docs/eluon.json")
            return 1
        print("docs/eluon.json 최신 상태입니다.")
        return 0

    target.write_text(text, encoding="utf-8")
    print(f"✓ docs/eluon.json — 자산 {len(out['assets'])}개 · "
          f"그룹 {len(out['groups'])}개 · 테마 {len(out['themes'])}개")
    if dropped:
        print(f"  deprecated 제외: {', '.join(dropped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

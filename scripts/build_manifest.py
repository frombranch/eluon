#!/usr/bin/env python3
"""
build_manifest.py — 사이드카 JSON들을 모아 manifest.json 과 index/ASSETS.md 를 만듭니다.

manifest.json 은 손으로 고치지 않습니다. 항상 이 스크립트가 생성합니다.

사용:
    python3 scripts/build_manifest.py
    python3 scripts/build_manifest.py --check   # 커밋본이 낡았으면 실패 (CI용)
"""
import json
import pathlib
import sys
from urllib.parse import quote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_tokens import load as load_tokens  # 테마별 크기 토큰을 해석하려고 씁니다

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
CHECK_ONLY = "--check" in sys.argv
SIZES = {}
# 라운드 눈금이 둘입니다. sm/md/lg 는 컨트롤(버튼·입력·칩), xl 은 컨테이너.
CONTAINER_GROUPS = {"card", "table", "modal", "feedback"}
BPS = {}


def cdn_url(rel_path: str) -> str:
    org, repo, ver = CONFIG["org"], CONFIG["repo"], CONFIG["version"]
    p = quote(rel_path)
    kind = CONFIG.get("cdn", "jsdelivr")
    if kind == "jsdelivr":
        return f"https://cdn.jsdelivr.net/gh/{org}/{repo}@{ver}/{p}"
    if kind == "raw":
        return f"https://raw.githubusercontent.com/{org}/{repo}/{ver}/{p}"
    if kind == "pages":
        return f"https://{org}.github.io/{repo}/{p}"
    raise ValueError(f"알 수 없는 cdn 설정: {kind}")


def foundation_maps():
    """테마별 파운데이션. 지금까지 manifest 에 활자·레이아웃이 아예 없어서,
    에이전트가 규격은 지키면서 위계와 폭은 매번 자기 기본값으로 그렸습니다."""
    out = {}
    for th in CONFIG["themes"]:
        tk = load_tokens(th)
        sem = tk["semantic"]
        out[th] = {
            "font": sem.get("font", {}),
            "typography": tk.get("typography", {}),
            "layout": sem.get("layout", {}),
            "text": sem.get("text", {}),
            "space": sem.get("space", {}),
            "elevation": sem.get("elevation", {}),
            "breakpoint": sem.get("breakpoint", {}),
            # 모션과 이미지도 실어야 manifest 만 읽는 경로에서 값이 보입니다.
            # 없으면 지속시간과 비율을 그 자리에서 지어냅니다.
            "motion": sem.get("motion", {}),
            "media": sem.get("media", {}),
        }
    return out


VALID_STATUS = {"measured", "partial", "estimated"}


def theme_status():
    """테마마다 얼마나 믿을 수 있는지. 산문으로만 적어 두면 검사할 수가 없습니다.

    measured  색·치수 모두 실측
    partial   색은 실측, 치수는 일부만
    estimated 색부터 추정 — 대외 제출물에 쓰지 않습니다
    """
    out, errs = {}, []
    for th in CONFIG["themes"]:
        if th == CONFIG["defaultTheme"]:
            out[th] = "measured"      # 자사 테마는 우리 값이 곧 정답입니다
            continue
        path = ROOT / "tokens" / f"theme-{th}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        s = d.get("$status")
        if s not in VALID_STATUS:
            errs.append(f"theme-{th}.json: $status 가 없거나 잘못됨 "
                        f"({s!r}) — {' · '.join(sorted(VALID_STATUS))} 중 하나여야 합니다")
            continue
        if not d.get("$measured"):
            errs.append(f"theme-{th}.json: $measured 가 없습니다 — "
                        f"무엇을 옮겼고 무엇을 안 옮겼는지 적어야 합니다")
        out[th] = s
    return out, errs


def size_maps():
    """테마별 치수 표. spec 이 가리킬 수 있는 이름을 전부 모읍니다.

    레이아웃 블록(헤더·히어로·푸터·CTA 띠)은 콘텐츠 폭 자체가 규격이라
    semantic.layout 의 container.max 를 spec 에 적습니다. 그래서 같이 봅니다.
    CSS 변수는 여전히 --size-* / --layout-* 로 나뉘어 나갑니다."""
    out = {}
    for th in CONFIG["themes"]:
        sem = load_tokens(th)["semantic"]
        m = dict(sem.get("size", {}))
        m.update(sem.get("layout", {}))
        out[th] = m
    return out


def bp_maps():
    """테마별 브레이크포인트 표. {테마: {'md': 768, ...}}"""
    return {th: load_tokens(th)["semantic"].get("breakpoint", {}) for th in CONFIG["themes"]}


def resolve_responsive(resp, bps):
    """{'md': 'fill'} → {768: 'fill'}. 테마가 브레이크포인트를 옮기면 따라갑니다."""
    out = {}
    for name, how in (resp or {}).items():
        px = bps.get(name)
        if px is None:
            continue
        out[px] = how
    return dict(sorted(out.items()))


def resolve_spec(spec, sizes):
    """spec 의 토큰명을 실제 수치로 바꿉니다. 토큰이 아닌 값은 그대로 둡니다."""
    out = {}
    for k, v in spec.items():
        out[k] = sizes[v] if isinstance(v, str) and v in sizes else v
    return out


def collect():
    assets, errors, seen = [], [], set()
    for sidecar in sorted((ROOT / "assets").rglob("*.json")):
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{sidecar.relative_to(ROOT)}: JSON 파싱 실패 — {e}")
            continue

        aid = data.get("id")
        if not aid:
            errors.append(f"{sidecar.relative_to(ROOT)}: id 없음")
            continue
        if aid in seen:
            errors.append(f"{aid}: ID 중복")
            continue
        seen.add(aid)
        if sidecar.stem != aid:
            errors.append(f"{aid}: 파일명({sidecar.stem})과 id가 다름")

        renders = data.get("renders") or {}
        missing = [t for t, p in renders.items() if not (ROOT / p).exists()]
        # 테마만 config 에 추가하고 렌더를 안 돌리면 사이드카에 그 키가 아예 없습니다.
        # 키가 없으면 위의 '이미지 없음' 검사가 작동하지 않아 그냥 통과합니다.
        untouched = [th for th in CONFIG["themes"] if th not in renders]
        if not renders:
            errors.append(f"{aid}: renders 없음")
            continue
        if missing:
            errors.append(f"{aid}: 렌더 이미지 없음 → {', '.join(missing)}")
            continue
        if untouched:
            errors.append(f"{aid}: 렌더 안 된 테마 → {', '.join(untouched)} (render.py 를 돌리세요)")
            continue

        data["cdn"] = {t: cdn_url(p) for t, p in renders.items()}
        data["specByTheme"] = {th: resolve_spec(data["spec"], sz)
                               for th, sz in SIZES.items()}
        data["responsiveByTheme"] = {th: resolve_responsive(data.get("responsive"), bp)
                                     for th, bp in BPS.items()}
        for th, bp in BPS.items():
            unknown = [n for n in (data.get("responsive") or {}) if n not in bp]
            if unknown:
                errors.append(f"{aid}: {th} 테마에 없는 브레이크포인트 → {', '.join(unknown)}")
        data["preview"] = data["cdn"].get(CONFIG["defaultTheme"])
        if not data.get("usage"):
            errors.append(f"{aid}: usage 비어 있음")
        # 컨테이너와 컨트롤은 라운드 눈금이 다릅니다. 알약 버튼을 쓰는 테마에서
        # 컨테이너가 lg 를 쓰면 표와 토스트까지 알약이 됩니다 (cobalt 에서 실제로 그랬습니다).
        if data["group"] in CONTAINER_GROUPS:
            r = data["spec"].get("radius")
            if r not in (None, "xl", "none"):
                errors.append(f"{aid}: 컨테이너인데 radius 가 '{r}' 입니다 — "
                              f"컨테이너는 xl 을 씁니다 (알약 테마에서 표·토스트가 알약이 됩니다)")
        if data.get("status") == "deprecated" and not data.get("replacedBy"):
            errors.append(f"{aid}: deprecated 인데 replacedBy 가 없음")
        if data.get("variantOf") and not data.get("variantState"):
            errors.append(f"{aid}: variantOf 는 있는데 variantState 가 없음")
        assets.append(data)

    # 상태는 자산이 아닙니다. 부모에 매답니다 — 목록에서는 빠지지만
    # 규격·토큰·이미지는 그대로 남습니다.
    by_id = {a["id"]: a for a in assets}
    for a in assets:
        pid = a.get("variantOf")
        if not pid:
            continue
        parent = by_id.get(pid)
        if parent is None:
            errors.append(f"{a['id']}: variantOf 가 가리키는 {pid} 가 없음")
            continue
        if parent.get("variantOf"):
            errors.append(f"{a['id']}: 변형의 변형은 만들지 않습니다 ({pid} 도 변형)")
            continue
        if a["group"] != parent["group"]:
            errors.append(f"{a['id']}: 부모({pid})와 group 이 다름")
        parent.setdefault("variants", []).append({
            "id": a["id"],
            "state": a["variantState"],
            "tokens": a.get("tokens", {}),
            "spec": a.get("spec", {}),
        })
        st = parent.setdefault("states", [])
        if a["variantState"] not in st:
            errors.append(f"{pid}: states 에 '{a['variantState']}' 가 없는데 "
                          f"{a['id']} 가 그 상태를 그립니다")
    for a in assets:
        if "variants" in a:
            a["variants"].sort(key=lambda v: v["id"])
    return assets, errors


def build_markdown(assets):
    top = [a for a in assets if not a.get("variantOf")]
    lines = [
        "# 자산 목록", "",
        f"`{CONFIG['org']}/{CONFIG['repo']}` · **{CONFIG['version']}** · "
        f"총 {len(top)}개(상태 변형 {len(assets) - len(top)}개 별도) · "
        f"테마 {', '.join(CONFIG['themes'])}", "",
        "> `scripts/build_manifest.py`가 생성합니다. 직접 고치지 마세요.",
        f"> 아래 규격은 **{CONFIG['defaultTheme']}** 테마 기준입니다. "
        "치수는 테마마다 다릅니다 — `manifest.json`의 `specByTheme`를 보십시오.", "",
    ]
    for group in sorted({a["group"] for a in top}):
        rows = sorted([a for a in top if a["group"] == group], key=lambda x: x["id"])
        lines += [f"## {group} ({len(rows)})", "",
                  "| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |", "|---|---|---|---|---|"]
        for a in rows:
            s = a.get("specByTheme", {}).get(CONFIG["defaultTheme"], a.get("spec", {}))
            size = " ".join(filter(None, [
                f"h{s['height']}" if "height" in s else "",
                f"w{s['width']}" if isinstance(s.get("width"), int) else "",
                f"r:{s['radius']}" if "radius" in s else "",
            ])) or "—"
            var = "".join(f" · `{v['id']}`" for v in a.get("variants", []))
            name = a["name"] + (f"<br><small>상태{var}</small>" if var else "")
            lines.append(f"| `{a['id']}` | {name} | {size} | {a['usage']} | {a.get('dont','')} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    global SIZES, BPS
    SIZES = size_maps()
    BPS = bp_maps()
    assets, errors = collect()
    # 파이프라인이 안 건드리는 수기 문서. 버전을 올리면 여기도 같이 고쳐야 하는데
    # 매번 빠뜨립니다. 실제로 v1.3.1 에서 config 만 되돌아가 태그와 내용이 어긋났습니다.
    #
    # 다만 문서 안의 버전이 전부 "지금 버전"이어야 하는 것은 아닙니다.
    # 사람이 복사해 쓰는 것 — CDN 주소와 clone 명령 — 만 틀리면 실제로 깨집니다.
    # "언제 바뀌었다"는 이력 서술까지 싸잡아 올리면 역사가 현재 버전으로 덮입니다.
    # 실제로 v1.12.0 에서 v1.11.1 이전의 변경 이력이 전부 v1.12.0 으로 바뀌었습니다.
    # 그래서 나누어 봅니다 — 따라 하면 깨지는 것은 실패, 나머지는 알림만.
    import re
    LIVE = re.compile(r"(?:@|--branch\s+)(v\d+\.\d+\.\d+)")
    ANY = re.compile(r"v\d+\.\d+\.\d+")
    version_notes = []
    for f in ["README.md", "CLAUDE.md", "prompts/01-시안제작.md", "prompts/03-일관성QA.md"]:
        path = ROOT / f
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        live_stale = sorted(set(LIVE.findall(text)) - {CONFIG["version"]})
        if live_stale:
            errors.append(f"{f}: 따라 하면 깨지는 버전이 있습니다 — {', '.join(live_stale)} "
                          f"(config 는 {CONFIG['version']}). CDN 주소와 clone 명령을 고치세요.")
        other_stale = sorted(set(ANY.findall(text)) - set(LIVE.findall(text))
                             - {CONFIG["version"]})
        if other_stale:
            version_notes.append(f"{f}: {', '.join(other_stale)}")

    # 몽타주 시트는 여기서 검사하지 않습니다 — make_montage.py 가 이 뒤에 돌기 때문에
    # 새 테마 첫 빌드가 반드시 실패합니다. 시트 검사는 build_docs.py(마지막 단계)에 있습니다.
    for th in CONFIG["themes"]:
        if not (ROOT / "docs" / "tokens" / f"eluon-{th}.css").exists():
            errors.append(f"docs/tokens/eluon-{th}.css 없음 (build_tokens.py 를 돌리세요)")
    if version_notes:
        print("알림 — 이력으로 보이는 옛 버전 표기가 있습니다. 사실이면 그대로 두세요:")
        for n in version_notes:
            print(f"  · {n}")
    if errors:
        print("빌드 실패:\n" + "\n".join(f"  ✗ {e}" for e in errors))
        return 1

    statuses, st_errs = theme_status()
    errors += st_errs
    foundation = foundation_maps()
    # 활자 역할이 빠지면 "어디에 쓰는 스타일인지" 를 다시 못 알려줍니다.
    for th, f in foundation.items():
        no_role = [k for k, v in f["typography"].items() if not v.get("role")]
        if no_role:
            errors.append(f"{th}: 활자 role 없음 → {', '.join(no_role)} (tokens 에 role 을 적으세요)")
    # 그룹 이름이 다섯 군데에 흩어져 있습니다 — 렌더 폴더 · 빌더 한글명 ·
    # 문서 한글명 · 문서 영문명 · 스키마 enum. 하나만 빠뜨리면 CI 에서만 터집니다.
    # 실제로 v1.10.0 에서 disclosure 를 스키마에 안 넣어 푸시 4건이 연달아 실패했습니다.
    try:
        sch = json.loads((ROOT / "schema" / "asset.schema.json").read_text(encoding="utf-8"))
        allowed = set(sch["properties"]["group"].get("enum") or [])
        used = {a["group"] for a in assets}
        gap = sorted(used - allowed)
        if gap:
            errors.append(f"schema/asset.schema.json 의 group enum 에 없는 그룹: "
                          f"{', '.join(gap)} — 여기에 추가하세요 (CI 가 이걸로 검사합니다)")
    except (OSError, KeyError) as e:
        errors.append(f"schema/asset.schema.json 을 읽지 못했습니다 — {e}")

    if errors:
        print("빌드 실패:\n" + "\n".join(f"  ✗ {e}" for e in errors))
        return 1

    manifest = {
        "$schema": "./schema/asset.schema.json",
        "name": "Eluon Design System",
        "version": CONFIG["version"],
        "repo": f"https://github.com/{CONFIG['org']}/{CONFIG['repo']}",
        "docs": f"https://{CONFIG['org']}.github.io/{CONFIG['repo']}/",
        "themes": CONFIG["themes"],
        "themeStatus": statuses,
        "defaultTheme": CONFIG["defaultTheme"],
        "tokens": {t: cdn_url(f"docs/tokens/eluon-{t}.css") for t in CONFIG["themes"]},
        "sheet": {t: cdn_url(f"index/sheet-{t}.png") for t in CONFIG["themes"]},
        "howToUse": "CLAUDE.md 를 먼저 읽으세요. 여기에 없는 ID는 사용하지 않습니다. "
                    "자산을 놓기 전에 foundationByTheme.<테마> 의 layout 과 typography 를 먼저 읽으세요.",
        "foundationByTheme": foundation,
        # 상태 변형은 자산 수에 넣지 않습니다. 목록이 부풀어 보입니다.
        "count": sum(1 for a in assets if not a.get("variantOf")),
        "variantCount": sum(1 for a in assets if a.get("variantOf")),
        "assets": assets,
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    md_text = build_markdown(assets)

    if CHECK_ONLY:
        stale = []
        mf = ROOT / "manifest.json"
        if not mf.exists() or mf.read_text(encoding="utf-8") != manifest_text:
            stale.append("manifest.json")
        idx = ROOT / "index" / "ASSETS.md"
        if not idx.exists() or idx.read_text(encoding="utf-8") != md_text:
            stale.append("index/ASSETS.md")
        if stale:
            print("커밋본이 낡았습니다. build_manifest.py 를 다시 돌리세요: " + ", ".join(stale))
            return 1
        print("manifest 최신 상태입니다.")
        return 0

    (ROOT / "manifest.json").write_text(manifest_text, encoding="utf-8")
    (ROOT / "index").mkdir(exist_ok=True)
    (ROOT / "index" / "ASSETS.md").write_text(md_text, encoding="utf-8")
    print(f"✓ manifest.json — 자산 {len(assets)}개")
    print("✓ index/ASSETS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

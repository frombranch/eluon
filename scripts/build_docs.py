#!/usr/bin/env python3
"""
build_docs.py — 공개 문서 사이트를 생성합니다. (GitHub Pages)

manifest와 레시피에서 직접 만들기 때문에, 문서가 자산과 어긋날 수 없습니다.
문서를 손으로 갱신하는 일은 없습니다.

산출: docs/index.html
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from recipes.components import BASE_CSS, build  # noqa: E402

CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
CORE = json.loads((ROOT / "tokens" / "core.json").read_text(encoding="utf-8"))
ELUO = json.loads((ROOT / "tokens" / "theme-eluo.json").read_text(encoding="utf-8"))

from build_pb_manifest import THEME_KO  # 테마 라벨은 한 곳에서만 관리합니다

GROUP_KO = {
    "button": "버튼", "chip": "칩", "input": "입력", "card": "카드",
    "navigation": "내비게이션", "table": "테이블", "feedback": "피드백",
    "badge": "뱃지", "modal": "모달", "commerce": "커머스", "layout": "레이아웃",
    "disclosure": "접기",
}

# 디스플레이 타입에 쓸 영문 이름. &shy;는 열 폭이 좁을 때만 하이픈으로 끊깁니다.
GROUP_EN = {
    "button": "But&shy;tons", "chip": "Chips", "input": "In&shy;puts", "card": "Cards",
    "navigation": "Navi&shy;gation", "table": "Tables", "feedback": "Feed&shy;back",
    "badge": "Badges", "modal": "Modals", "disclosure": "Dis&shy;closure",
}


def scope_css(css: str, prefix: str) -> str:
    """컴포넌트 CSS의 선택자를 #prefix 안으로 가둡니다. 문서 페이지에서 서로 충돌하지 않도록."""
    out = []
    for block in css.split("}"):
        if "{" not in block:
            continue
        sel, body = block.split("{", 1)
        sels = [f"#{prefix} {s.strip()}" if s.strip() not in ("html", "body")
                else f"#{prefix}" for s in sel.split(",") if s.strip()]
        out.append(", ".join(sels) + "{" + body + "}")
    return "".join(out)


def theme_css(theme: str) -> str:
    raw = (ROOT / "docs" / "tokens" / f"eluon-{theme}.css").read_text(encoding="utf-8")
    return re.sub(r":root\s*\{", f'[data-eluon-theme="{theme}"]{{', raw, count=1)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def theme_primitives(theme: str) -> dict:
    """core 위에 테마 프리미티브를 얹은 결과. 계열 안에서 단계 단위로 덮어씁니다."""
    t = json.loads((ROOT / "tokens" / f"theme-{theme}.json").read_text(encoding="utf-8"))
    merged = {fam: dict(steps) for fam, steps in CORE["primitive"].items()}
    for fam, steps in t.get("primitive", {}).items():
        merged.setdefault(fam, {}).update(steps)
    return merged


def swatches():
    """테마마다 한 벌씩 찍고 활성 테마 것만 CSS 로 보입니다.

    core 값을 그대로 구워 넣으면 하버·엠버처럼 gray 를 덮어쓰는 테마에서
    화면 값이 틀립니다. 테마가 더한 브랜드 계열(taupe·navy…)도 사라집니다.
    헥스 글자까지 맞춰야 하므로 CSS 변수 하나로는 안 되고, 벌을 나눕니다.
    """
    core = CORE["primitive"]
    sets = []
    for theme in CONFIG["themes"]:
        prim = theme_primitives(theme)
        # 테마가 더한 계열을 앞에. 그 테마를 그 테마답게 만드는 색이라서.
        fams = ([f for f in prim if f not in core] +
                [f for f in prim if f in core])
        rows = []
        for family in fams:
            steps = prim[family]
            added = family not in core
            over = [k for k, v in steps.items() if core.get(family, {}).get(k) != v]
            chips = []
            for k, v in steps.items():
                cv = core.get(family, {}).get(k)
                mark = ' class="sw ovr"' if (not added and cv != v) else ' class="sw"'
                tip = (f' title="코어 {cv} 에서 덮어썼습니다"' if (not added and cv) else
                       f' title="코어에 없는 단계입니다"' if (not added and cv is None) else "")
                chips.append(f'<div{mark}{tip}><span style="background:{v}"></span>'
                             f'<code>{family}.{k}</code><em>{v}</em></div>')
            if added:
                tag = '<span class="swtag">테마 추가</span>'
                note = ""
            elif over:
                tag = f'<span class="swtag">코어에서 {len(over)}개 덮어씀</span>'
                note = '<p class="swnote">* 표시가 코어와 다른 값입니다.</p>'
            else:
                tag, note = "", ""
            rows.append(f'<div class="swrow"><h4>{family}{tag}</h4>'
                        f'<div class="swgrid">{"".join(chips)}</div>{note}</div>')
        sets.append(f'<div class="swset" data-theme="{theme}">{"".join(rows)}</div>')
    return "".join(sets)


def resolve_ref(ref, tokens):
    """{primitive.blue.500} → 실제 헥스. 스와치가 현재 테마를 따라가지 않도록 값으로 고정합니다."""
    m = re.match(r"^\{primitive\.([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\}$", str(ref))
    if not m:
        return None
    fam, step = m.groups()
    return tokens.get("primitive", {}).get(fam, {}).get(step)


def semantic_table():
    eluo_prims = {**CORE["primitive"], **ELUO.get("primitive", {})}
    rows = []
    for key, val in CORE["semantic"]["color"].items():
        core_hex = resolve_ref(val, CORE)
        over = ELUO["semantic"]["color"].get(key)
        over_hex = resolve_ref(over, {"primitive": eluo_prims}) if over else None
        core_cell = (f'<span class="dot" style="background:{core_hex}"></span>'
                     if core_hex else "") + f"<code>{esc(val)}</code>"
        eluo_cell = ((f'<span class="dot" style="background:{over_hex}"></span>'
                      if over_hex else "") + f"<code>{esc(over)}</code>") if over else "<em>동일</em>"
        rows.append(f"<tr><td><code>color.{esc(key)}</code></td>"
                    f"<td>{core_cell}</td><td>{eluo_cell}</td></tr>")
    return "".join(rows)


def type_scale():
    rows = ['<thead><tr><td>토큰</td><td>어디에 쓰나</td><td>보기</td>'
            '<td>size / weight / lh / tracking</td></tr></thead>']
    for name, d in CORE["typography"].items():
        rows.append(
            f'<tr><td><code>{name}</code></td>'
            f'<td>{esc(d.get("role",""))}</td>'
            f'<td style="font-size:{d["size"]}px;font-weight:{d["weight"]};'
            f'line-height:{d["lineHeight"]};letter-spacing:{d["tracking"]}">'
            f'디자인은 판단이다 Design</td>'
            f'<td class="n">{d["size"]} / {d["weight"]} / {d["lineHeight"]} / '
            f'{d["tracking"]}</td></tr>')
    return "".join(rows)


LAYOUT_KO = {
    "container.max":     ("콘텐츠 최대폭",   "캔버스가 더 넓어도 본문은 이 폭 안에 둡니다."),
    "container.gutter":  ("좌우 거터",       "화면 가장자리와 콘텐츠 사이 최소 여백."),
    "grid.columns":      ("그리드 열",       "본문 영역을 나누는 열 수."),
    "grid.gap":          ("열 간격",         "열과 열 사이."),
    "section.padY":      ("섹션 상하 여백",  "lg 이상에서. 섹션마다 다르게 주지 않습니다."),
    "section.padYSm":    ("섹션 상하 (sm)",  "sm 미만에서."),
    "section.headGap":   ("제목 ↔ 본문",     "섹션 제목과 그 아래 내용 사이."),
    "block.gap":         ("블록 간격",       "문단·블록 사이 기본값."),
    "card.gap":          ("카드 간격",       "카드 그리드의 가로·세로 간격."),
    "text.measure":      ("본문 한 줄 길이",  "글자수(ch). 넘기면 읽기 어려워집니다."),
}


def layout_table():
    """레이아웃이 시스템에 없어서, 규격은 맞는데 폭도 리듬도 없는 화면이 나왔습니다."""
    rows = ['<thead><tr><td>토큰</td><td>무엇</td><td>값</td><td>왜</td></tr></thead>']
    lay = CORE["semantic"].get("layout", {})
    for key, val in lay.items():
        ko, why = LAYOUT_KO.get(key, (key, ""))
        unit = "" if key == "grid.columns" else ("ch" if key == "text.measure" else "px")
        rows.append(f'<tr><td><code>layout.{esc(key)}</code></td><td>{esc(ko)}</td>'
                    f'<td class="n">{val}{unit}</td><td>{esc(why)}</td></tr>')
    return "".join(rows)


TEXT_KO = {
    "break":        ("어절 단위 줄바꿈", "한글 낱자 중간에서 자르지 않습니다."),
    "overflowWrap": ("긴 문자열만 끊기", "keep-all 만 두면 긴 영문·URL 이 넘칩니다. 둘은 짝입니다."),
    "wrap":         ("줄 끝 고르게",     "마지막 줄에 한 어절만 남는 것을 줄입니다."),
    "numeric":      ("숫자 자릿수 맞춤",  "한글 사이에 낀 숫자가 흔들리지 않습니다."),
}


def text_table():
    """한글 조판. 시스템에 규칙이 없으면 화면마다 다르게 끊깁니다."""
    rows = ['<thead><tr><td>토큰</td><td>무엇</td><td>값</td><td>왜</td></tr></thead>']
    for key, val in CORE["semantic"].get("text", {}).items():
        ko, why = TEXT_KO.get(key, (key, ""))
        rows.append(f'<tr><td><code>text.{esc(key)}</code></td><td>{esc(ko)}</td>'
                    f'<td><code>{esc(val)}</code></td><td>{esc(why)}</td></tr>')
    return "".join(rows)


def space_table():
    rows = ['<thead><tr><td>토큰</td><td>값</td><td>보기</td></tr></thead>']
    for key, val in CORE["semantic"]["space"].items():
        rows.append(f'<tr><td><code>space.{esc(key)}</code></td><td class="n">{val}px</td>'
                    f'<td><span style="display:inline-block;height:12px;width:{val}px;'
                    f'background:var(--color-brand-primary)"></span></td></tr>')
    return "".join(rows)


def elevation_table():
    rows = ['<thead><tr><td>토큰</td><td>보기</td></tr></thead>']
    for key, val in CORE["semantic"]["elevation"].items():
        box = ("" if val == "none" else f"box-shadow:{val};")
        rows.append(f'<tr><td><code>elevation.{esc(key)}</code></td>'
                    f'<td><span style="display:inline-block;width:72px;height:34px;'
                    f'background:var(--color-bg-surface);border:1px solid var(--color-border-subtle);'
                    f'{box}"></span></td></tr>')
    return "".join(rows)


def state_previews(vars_, by_id, css):
    """상태 변형 미리보기. 부모 카드 안에 라벨과 함께 나란히 놓습니다."""
    if not vars_:
        return ""
    tiles = []
    for v in sorted(vars_, key=lambda x: x["id"]):
        vid = "cmp-" + v["id"]
        css.append(scope_css(v["css"], vid))
        state = by_id.get(v["id"], {}).get("variantState", "")
        tiles.append(f'<div class="stile"><div class="slabel">{esc(state)}</div>'
                     f'<div class="preview"><div id="{vid}">{v["html"]}</div></div>'
                     f'<div class="sid">{esc(v["id"])}</div></div>')
    return ('<div class="states-row"><div class="shd">상태</div>'
            f'<div class="stiles">{"".join(tiles)}</div></div>')


def sec_head(label, title_en, ko, desc):
    """구다이 스타일 섹션 머리: 레이블+대형 영문 / 리드 / 설명 3열."""
    return f"""<div class="sec-head">
  <div class="col-a"><span class="lbl">{label}</span><h2 lang="en">{title_en}</h2></div>
  <div class="col-b"><span class="lbl" aria-hidden="true"></span><p class="lead">{ko}</p></div>
  <div class="col-b"><span class="lbl" aria-hidden="true"></span><p class="body-t">{desc}</p></div>
</div>"""


def component_sections(comps, manifest):
    by_id = {a["id"]: a for a in manifest["assets"]}
    by_cid = {c["id"]: c for c in comps}
    html, css = [], []
    # 상태는 자산이 아닙니다. 부모 카드 안에 나란히 넣습니다.
    variants = {}
    for c in comps:
        pid = by_id.get(c["id"], {}).get("variantOf")
        if pid:
            variants.setdefault(pid, []).append(c)
    for group in sorted({c["group"] for c in comps}):
        items = [c for c in comps if c["group"] == group
                 and not by_id.get(c["id"], {}).get("variantOf")]
        if not items:
            continue
        cards = []
        for c in sorted(items, key=lambda x: x["id"]):
            a = by_id[c["id"]]
            pid = "cmp-" + c["id"]
            css.append(scope_css(c["css"], pid))
            spec_rows = "".join(
                f"<tr><td>{esc(k)}</td><td class='n'>{esc(v)}</td></tr>"
                for k, v in c["spec"].items())
            token_rows = "".join(
                f"<tr><td>{esc(k)}</td><td><code>{esc(v)}</code></td></tr>"
                for k, v in c.get("tokens", {}).items())
            states = " · ".join(esc(s) for s in c.get("states", []))
            cards.append(f"""
<article class="cmp" id="{c['id']}" data-r>
  <div class="c-meta">
    <label class="pick"><input type="checkbox" class="pickbox" value="{c['id']}"
      aria-label="{esc(c['name'])} 고르기"><span>고르기</span></label>
    <h3>{esc(c['name'])}</h3>
    <p class="cid">{c['id']}</p>
    <p class="states">{states}</p>
  </div>
  <div class="c-body">
    <div class="preview"><div id="{pid}">{c['html']}</div></div>
      {state_previews(variants.get(c['id'], []), by_id, css)}
    <div class="c-detail">
      <div class="usage">
        <p class="use"><b>언제</b>{esc(c['usage'])}</p>
        <p class="dont"><b>금지</b>{esc(c.get('dont',''))}</p>
      </div>
      <div class="specs"><table><caption>spec</caption><tbody>{spec_rows}</tbody></table></div>
      <div class="specs"><table><caption>tokens</caption><tbody>{token_rows}</tbody></table></div>
    </div>
    <details class="url"><summary>자산 URL</summary>
      <pre>{esc(a['cdn'][CONFIG['defaultTheme']])}</pre>
    </details>
  </div>
</article>""")
        head = sec_head(
            "Components",
            GROUP_EN.get(group, group.capitalize()),
            f"{GROUP_KO.get(group, group)} {len(items)}종",
            "규격과 토큰은 manifest가 정답입니다. 이미지에서 눈대중으로 재지 않습니다.")
        html.append(f'<section class="sec" id="g-{group}">{head}'
                    f'<div class="cmps">{"".join(cards)}</div></section>')
    return "".join(html), "\n".join(css)


SITE_CSS = """/* ── 문서 사이트 껍데기 (컴포넌트 토큰과 분리) ──────────────────────────
   무채색 · 헤어라인 그리드 · 대형 영문 그로테스크. 라운드와 그림자는 쓰지 않습니다.
   컴포넌트 프리뷰 안쪽은 manifest의 spec을 그대로 따르므로 여기서 건드리지 않습니다. */
:root{
  --pg:#FFFFFF; --tx:#141414; --tx2:#757575; --ln:#DCDCDC; --ln2:#141414;
  --pad:clamp(20px,5vw,120px);
  --disp:'Helvetica Neue',Helvetica,Arial,'Pretendard Variable',Pretendard,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root{--pg:#0A0A0A;--tx:#F0F0F0;--tx2:#78787E;--ln:#2B2B2B;--ln2:#F0F0F0}
}
body{background:var(--pg);color:var(--tx);
  font-family:'Pretendard Variable',Pretendard,-apple-system,'Apple SD Gothic Neo',sans-serif;
  line-height:1.65;letter-spacing:-.01em;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{padding:0 var(--pad)}

/* 상단 고정 바 */
.barwrap{position:sticky;top:0;z-index:20;margin:0 calc(var(--pad) * -1)}
.bar{display:flex;align-items:center;gap:28px;
  height:66px;padding:0 var(--pad);
  background:color-mix(in srgb,var(--pg) 88%,transparent);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--ln2)}
/* 색만 바뀌면 어느 테마를 보고 있는지 알 수 없습니다. 이름과 성격을 글로 답니다. */
.themestrip{display:flex;align-items:baseline;gap:10px;padding:9px var(--pad);
  background:color-mix(in srgb,var(--pg) 88%,transparent);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--ln);font-size:12.5px;line-height:1.5;
  white-space:nowrap;overflow:hidden}
.themestrip .tskey{font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--tx2);font-weight:700;flex:none}
.themestrip b{font-weight:700;flex:none}
.themestrip span.tshint{color:var(--tx2);overflow:hidden;text-overflow:ellipsis}
.logo{font-family:var(--disp);font-size:19px;font-weight:700;letter-spacing:-.03em;
  text-decoration:none;flex:none}
.bar nav{display:flex;gap:24px;flex-wrap:wrap;margin:0 auto}
.bar nav a{color:var(--tx);text-decoration:none;font-size:14px;font-weight:600}
.bar nav a:hover{color:var(--tx2)}
/* 다른 페이지로 나가는 링크. 섹션 앵커와 성격이 달라 세로줄로 갈라 둡니다. */
.bar nav.pages{margin:0;flex:none;gap:18px;padding-left:22px;
  border-left:1px solid var(--ln)}
.bar nav.pages a{font-size:13px;color:var(--tx2)}
.bar nav.pages a:hover{color:var(--tx)}
.themes{display:flex;flex:none}
.navtog{display:none;flex:none;margin-left:auto;width:40px;height:40px;
  align-items:center;justify-content:center;padding:0;
  border:1px solid var(--ln2);background:transparent;color:var(--tx);cursor:pointer}
/* 좁은 화면 — 링크와 테마 전환을 햄버거 안으로 접습니다. */
@media(max-width:899px){
  .navtog{display:inline-flex}
  .barmenu{display:none;position:absolute;top:100%;left:0;right:0;z-index:19;
    flex-direction:column;background:var(--pg);
    max-height:calc(100dvh - 66px);overflow-y:auto;
    border-bottom:1px solid var(--ln2);padding:4px var(--pad) 20px}
  .barmenu[data-open]{display:flex}
  .bar nav{flex-direction:column;gap:0;margin:0}
  /* 접힌 메뉴에서는 세로줄이 의미가 없습니다. 위쪽 경계로 갈라 둡니다. */
  .bar nav.pages{padding-left:0;border-left:0;border-top:1px solid var(--ln2);
    margin-top:10px;padding-top:4px}
  .bar nav a{padding:13px 0;border-bottom:1px solid var(--ln)}
  /* 접힌 메뉴 안에서도 같은 처리 — 줄바꿈에 맡기면 가로 경계가 두 겹이 됩니다. */
  .barmenu .themes{display:grid;grid-template-columns:repeat(3,1fr);margin-top:18px;
    border-top:1px solid var(--ln2);border-left:1px solid var(--ln2)}
  .barmenu .themes button{margin:0;border:0;
    border-right:1px solid var(--ln2);border-bottom:1px solid var(--ln2)}
}
/* 넓은 화면에서는 같은 마크업을 왼쪽 레일로 세웁니다.
   가로 바에 링크 14개를 늘어놓으면 하나하나가 작아지고 순서가 안 읽힙니다.
   순서는 고르는 차례 그대로 — 로고 → 테마 → 지금 테마 → 링크. */
@media(min-width:900px){
  :root{--pad:clamp(24px,3vw,72px);--rail:236px}
  .barwrap{position:fixed;top:0;left:0;bottom:0;width:var(--rail);margin:0;
    display:flex;flex-direction:column;overflow-y:auto;
    background:var(--pg);border-right:1px solid var(--ln2)}
  /* 바와 메뉴는 껍데기만 벗겨 레일이 직접 순서를 잡게 합니다. */
  .bar,.barmenu{display:contents}
  .logo{order:1;padding:28px 24px 20px}
  .barwrap .themes{order:2;margin:0 24px;
    display:grid;grid-template-columns:1fr 1fr;
    border-top:1px solid var(--ln2);border-left:1px solid var(--ln2)}
  /* 헤어라인이 겹쳐 두 줄로 보이던 것 — 바깥은 컨테이너가, 안쪽은 칸의 오른쪽·아래만. */
  .barwrap .themes button{margin:0;border:0;
    border-right:1px solid var(--ln2);border-bottom:1px solid var(--ln2)}
  .themestrip{order:3;margin:16px 0 0;padding:14px 24px;
    flex-direction:column;align-items:flex-start;gap:2px;
    white-space:normal;overflow:visible;font-size:11.5px;line-height:1.5;
    border-top:1px solid var(--ln);border-bottom:1px solid var(--ln);backdrop-filter:none}
  .themestrip span.tshint{overflow:visible;text-overflow:clip;line-height:1.5}
  .bar nav{order:4;flex-direction:column;gap:0;margin:0;padding:20px 24px 28px;width:auto}
  .bar nav a{display:block;padding:7px 0;font-size:14px}
  .wrap{margin-left:var(--rail)}
  .sec{scroll-margin-top:28px}
}
.themes button{font:inherit;font-size:12px;font-weight:700;padding:7px 14px;
  border:1px solid var(--ln2);background:transparent;color:var(--tx);
  cursor:pointer;margin-left:-1px}
.themes button[aria-pressed="true"]{background:var(--ln2);color:var(--pg)}

/* 히어로 */
header.site{padding:clamp(24px,4.3vh,50px) 0 clamp(72px,11vh,130px)}
h1{font-family:var(--disp);font-weight:700;font-size:clamp(40px,7.5vw,112px);
  line-height:.9;letter-spacing:-.045em;margin:0}
.hero-b{display:grid;grid-template-columns:1fr;gap:22px 48px;margin-top:clamp(40px,6vh,72px)}
@media(min-width:900px){.hero-b{grid-template-columns:minmax(240px,1fr) 1.1fr 1.1fr}}
.lead{font-size:clamp(18px,2vw,23px);font-weight:700;letter-spacing:-.03em;
  line-height:1.5;margin:0;max-width:24ch}
.body-t{font-size:14.5px;color:var(--tx2);line-height:1.85;margin:0;max-width:44ch}
/* 한글은 기본값이 어절 중간에서도 끊깁니다. "만든 자/산" 같은 줄바꿈을 막습니다. */
.lead,.body-t{word-break:keep-all;text-wrap:pretty}
/* 문서 사이트도 같은 규칙으로. 한 군데씩 고치면 계속 새어 나옵니다. */
p,li,dd,h3,h4,.use,.dont,caption{word-break:keep-all;text-wrap:pretty}
/* 히어로는 폭 제한을 걸지 않습니다. 문장이 짧아 열 안에서 한 줄로 앉습니다. */
.hero-b .lead,.hero-b .body-t{max-width:none}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  margin:clamp(52px,8vh,88px) 0 0;border-top:1px solid var(--ln2)}
.meta div{padding:18px 20px 0;border-right:1px solid var(--ln)}
.meta div:first-child{padding-left:0}
.meta div:last-child{border-right:0}
.meta dt{font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--tx2);font-weight:700}
.meta dd{margin:8px 0 0;font-family:var(--disp);font-size:clamp(26px,3vw,36px);
  font-weight:700;letter-spacing:-.03em;line-height:1}
.meta dd a{text-decoration:none;border-bottom:2px solid var(--tx)}

/* 섹션 머리 */
.sec{padding:clamp(70px,10vh,120px) 0 0;scroll-margin-top:116px}
.sec-head{display:grid;grid-template-columns:1fr;gap:24px 48px}
@media(min-width:900px){.sec-head{grid-template-columns:minmax(240px,1fr) 1.1fr 1.1fr}}
.sec-head .lbl{display:block;font-size:13px;font-weight:700;padding-bottom:14px;
  border-bottom:1px solid var(--ln2)}
.sec-head .col-b{border-top:1px solid var(--ln2);padding-top:20px}
.sec-head .lbl:empty{display:none}
/* 3열로 펼쳐질 때만 — 빈 레이블이 자리를 잡아 세 열의 헤어라인이 같은 줄에 놓입니다. */
@media(min-width:900px){
  .sec-head .col-b{border-top:0;padding-top:0}
  .sec-head .lbl:empty{display:block}
  .sec-head .lbl:empty::before{content:"\\00a0"}
  .sec-head .col-b p{margin-top:20px}
}
h2{font-family:var(--disp);font-weight:700;font-size:clamp(44px,7.5vw,96px);
  line-height:.88;letter-spacing:-.045em;margin:24px 0 0;
  hyphens:manual;overflow-wrap:break-word}
h3{font-size:17px;font-weight:700;letter-spacing:-.02em;margin:0}
h4{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--tx);margin:0 0 14px;padding-bottom:12px;border-bottom:1px solid var(--ln2)}
/* 표만 있으면 "이 숫자를 어디에 쓰나" 가 안 보입니다. 표 위에 한 줄로 답니다. */
p.note{font-size:14px;line-height:24px;color:var(--tx2);margin:-4px 0 18px;
  max-width:76ch;word-break:keep-all;text-wrap:pretty}

/* 상태는 자산이 아니라 부모의 변형입니다. 카드 안에 함께 둡니다. */
.states-row{margin-top:20px;padding-top:16px;border-top:1px solid var(--ln)}
.shd{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--tx2);margin-bottom:12px}
.stiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:12px}
.stile{display:flex;flex-direction:column;gap:6px;min-width:0}
.slabel{font-size:12px;font-weight:700;color:var(--tx)}
.stile .preview{margin:0;overflow-x:auto;padding:24px 16px;min-height:0}
.sid{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--tx2);
  overflow:hidden;text-overflow:ellipsis}

/* 고르기 → 빌더. 링크만 걸어두면 보러 갔다가 돌아올 길이 없습니다. */
.pick{display:inline-flex;align-items:center;gap:6px;margin-bottom:10px;
  font-size:12px;color:var(--tx2);cursor:pointer;user-select:none}
.pick input{width:15px;height:15px;accent-color:var(--tx);cursor:pointer;margin:0}
.cmp:has(.pickbox:checked){outline:2px solid var(--ln2);outline-offset:8px}
.cmp:has(.pickbox:checked) .pick{color:var(--tx);font-weight:700}
.sendbar{
  position:fixed;left:50%;transform:translateX(-50%);bottom:24px;z-index:40;
  display:flex;align-items:center;gap:16px;max-width:calc(100vw - 32px);
  background:var(--tx);color:var(--pg);padding:12px 12px 12px 20px;
}
.sendbar[hidden]{display:none}
.sbcount{font-size:13px;white-space:nowrap}
.sbids{font-family:ui-monospace,Menlo,monospace;font-size:11px;opacity:.6;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:38vw}
.sbclear,.sbgo{
  font-family:inherit;font-size:13px;font-weight:600;padding:8px 14px;
  border:1px solid var(--pg);background:transparent;color:var(--pg);cursor:pointer;
  text-decoration:none;white-space:nowrap;
}
.sbgo{background:var(--pg);color:var(--tx)}
@media (max-width:640px){ .sbids{display:none} }

/* 표 · 코드 */
code{font-family:ui-monospace,Menlo,monospace;font-size:.86em;
  background:none;border:0;padding:0;color:var(--tx2)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
caption{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--tx);font-weight:700;padding-bottom:10px}
td{padding:8px 12px 8px 0;border-bottom:1px solid var(--ln);vertical-align:top}
td:last-child{padding-right:0}
td.n{font-variant-numeric:tabular-nums;color:var(--tx2);text-align:right}
.tw{overflow-x:auto;border-top:1px solid var(--ln2);margin-top:16px}
/* 예외 — h4 바로 아래 표는 h4의 선을 쓰고 자기 선을 지웁니다. 검은 선이 두 줄로 겹치지 않게. */
h4 + .tw{border-top:0;margin-top:0}
.tw thead td{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--tx2)}

/* 아이콘 — 채우지 않고, 선으로, 70% 로. 값은 토큰에서 옵니다. */
/* lucide.createIcons() 는 <i data-lucide> 를 <svg class="lucide …"> 로 바꿉니다.
   생성 전후 둘 다 잡아야 규칙이 적용됩니다. */
[data-lucide],svg.lucide{fill:var(--icon-fill,none);stroke:currentColor;
  stroke-width:var(--icon-strokewidth,1.2);opacity:var(--icon-opacity,.7)}
.icons{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));
  border-top:1px solid var(--ln);border-left:1px solid var(--ln)}
.icons div{display:flex;flex-direction:column;align-items:center;gap:10px;
  padding:22px 12px;border-right:1px solid var(--ln);border-bottom:1px solid var(--ln)}
.icons b{font-size:11px;font-weight:600;color:var(--tx2);letter-spacing:.02em}
.iconrule td:first-child{width:34%}

/* 스와치 */
.swrow{margin-top:44px}
.swgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));
  border-top:1px solid var(--ln);border-left:1px solid var(--ln)}
.sw{display:flex;align-items:center;gap:10px;font-size:12px;padding:12px 14px;
  border-right:1px solid var(--ln);border-bottom:1px solid var(--ln)}
.sw span{width:20px;height:20px;border:1px solid var(--ln);flex:none}
.sw em{font-style:normal;color:var(--tx2);font-variant-numeric:tabular-nums;margin-left:auto}
/* 테마마다 한 벌씩 있고, 활성 테마 것만 보입니다. 규칙은 build_docs.py 가 붙입니다. */
.swset{display:none}
.swtag{margin-left:10px;font-weight:400;text-transform:none;letter-spacing:0;
  font-size:11px;color:var(--tx2)}
.swnote{margin-top:10px;font-size:12px;color:var(--tx2)}
.sw.ovr code:after{content:"*";margin-left:2px;color:var(--tx2)}
.dot{display:inline-block;width:11px;height:11px;border:1px solid var(--ln);
  margin-right:7px;vertical-align:-1px}

/* 컴포넌트 */
.cmps{margin-top:clamp(48px,8vh,88px)}
.cmp{display:grid;grid-template-columns:1fr;gap:24px;
  border-top:1px solid var(--ln);padding:32px 0 40px}
@media(min-width:900px){
  .cmp{grid-template-columns:240px 1fr;gap:0}
  .c-body{border-left:1px solid var(--ln);padding-left:44px}
  .c-meta{padding-right:32px}
}
.cid{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;
  color:var(--tx2);margin:7px 0 0}
.states{margin:16px 0 0;font-size:11px;font-weight:600;letter-spacing:.05em;
  text-transform:uppercase;color:var(--tx2);line-height:1.9}
/* 프리뷰는 spec 대로의 실제 폭을 가집니다. 화면보다 넓으면 페이지가 아니라 이 상자가 스크롤합니다. */
.c-body{min-width:0}
.preview{display:flex;align-items:center;justify-content:safe center;min-height:160px;
  padding:44px 24px;border:1px solid var(--ln);background:#FFFFFF;overflow-x:auto}
.c-detail{display:grid;grid-template-columns:1fr;gap:26px 40px;margin-top:32px}
@media(min-width:760px){.c-detail{grid-template-columns:1fr 1fr}}
@media(min-width:1180px){.c-detail{grid-template-columns:1.2fr 1fr 1fr}}
.usage p{margin:0 0 16px;font-size:14px;color:var(--tx2);line-height:1.75}
.usage b{display:block;font-size:11px;letter-spacing:.08em;color:var(--tx);
  font-weight:700;margin-bottom:4px}
.specs td{padding:6px 12px 6px 0}
/* 레일이 생겨 본문이 좁아지면서 드러난 넘침 — 그리드 칸은 기본이 min-width:auto 라
   표가 칸보다 넓어지면 페이지가 밀립니다. 칸은 줄어들 수 있게, 긴 토큰명은 접히게. */
.c-detail>*{min-width:0}
.specs td{overflow-wrap:anywhere}
.url{margin-top:26px;font-size:12.5px;color:var(--tx2)}
.url summary{cursor:pointer;font-weight:600;color:var(--tx)}
.url pre{margin:12px 0 0;padding:14px 16px;border:1px solid var(--ln);
  overflow-x:auto;font-size:11.5px;font-family:ui-monospace,Menlo,monospace}
pre.prompt{padding:26px 28px;border:1px solid var(--ln);font-size:13px;line-height:1.85;
  font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap;overflow-x:auto}

/* 맨 위로 — 스크롤이 길어 아래에서 올라올 방법이 필요합니다. */
.totop{position:fixed;right:clamp(16px,3vw,40px);bottom:clamp(16px,3vw,40px);z-index:30;
  width:48px;height:48px;display:flex;align-items:center;justify-content:center;padding:0;
  border:1px solid var(--ln2);background:var(--pg);color:var(--tx);cursor:pointer;
  opacity:0;transform:translateY(8px);pointer-events:none;
  transition:opacity .25s ease,transform .25s ease}
.totop.on{opacity:1;transform:none;pointer-events:auto}
.totop:hover{background:var(--ln2);color:var(--pg)}

footer{margin-top:clamp(90px,14vh,160px);padding:26px 0 72px;
  border-top:1px solid var(--ln2);font-size:12.5px;color:var(--tx2);
  display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap}

/* 스크롤 등장 */
[data-r]{opacity:0;transform:translateY(28px);
  transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
[data-r].in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){
  [data-r]{opacity:1;transform:none;transition:none}
}"""


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    comps = build(CORE)
    sections, comp_css = component_sections(comps, manifest)
    # 예전엔 core·eluo 두 테마만 하드코딩돼 있어서 세 번째 테마는 문서 사이트에서
    # CSS 도 버튼도 없었습니다. CONFIG 를 따라가게 고칩니다.
    all_theme_css = "\n".join(theme_css(t_) for t_ in CONFIG["themes"])
    swset_css = "".join(f'[data-eluon-theme="{t_}"] .swset[data-theme="{t_}"]{{display:block}}'
                        for t_ in CONFIG["themes"])
    theme_btns = "".join(
        f'<button data-theme="{t_}" aria-pressed="{str(t_ == CONFIG["defaultTheme"]).lower()}"'
        f' data-hint="{THEME_KO.get(t_, (t_, ""))[1]}"'
        f' title="{THEME_KO.get(t_, (t_, ""))[0]} — {THEME_KO.get(t_, (t_, ""))[1]}">'
        f'{THEME_KO.get(t_, (t_, ""))[0]}</button>'
        for t_ in CONFIG["themes"])
    dflt = CONFIG["defaultTheme"]
    dflt_label, dflt_hint = THEME_KO.get(dflt, (dflt, ""))
    nav = "".join(f'<a href="#g-{g}">{GROUP_KO.get(g,g)}</a>'
                  for g in sorted({c["group"] for c in comps}))

    page = f"""<!doctype html>
<html lang="ko" data-eluon-theme="{CONFIG['defaultTheme']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eluon — Design System</title>
<meta name="description" content="디자인포지션의 에이전틱 디자인 시스템. 컴포넌트 {manifest['count']}개, 테마 {len(CONFIG['themes'])}종.">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
<style>
{all_theme_css}
{BASE_CSS}
{comp_css}

{SITE_CSS}
{swset_css}
</style>
</head>
<body>
<div class="wrap">

<div class="barwrap">
<div class="bar">
  <a class="logo" href="#top">eluon</a>
  <button class="navtog" id="navtog" type="button"
    aria-expanded="false" aria-controls="barmenu" aria-label="메뉴 열기"><i data-lucide="menu"></i></button>
  <div class="barmenu" id="barmenu">
    <nav><a href="#foundation">파운데이션</a>{nav}<a href="#agent">에이전트</a></nav>
    <nav class="pages" aria-label="다른 페이지">
      <a href="guide.html">사용설명서</a><a href="prompt-builder.html">프롬프트 빌더</a>
    </nav>
    <div class="themes" role="group" aria-label="테마 전환">
      {theme_btns}
    </div>
  </div>
</div>
<p class="themestrip" aria-live="polite">
  <span class="tskey">Theme</span><b id="themeName">{dflt_label}</b>
  <span class="tshint" id="themeHint">{dflt_hint}</span>
</p>
</div>

<header class="site" id="top" data-r>
  <h1 lang="en">Design System</h1>
  <div class="hero-b">
    <div></div>
    <div><p class="lead">에이전트가 읽고 조립하는 자산 라이브러리입니다.</p></div>
    <div><p class="body-t">정의가 그대로 이미지가 되므로 문서와 자산이 어긋나지 않습니다.</p></div>
  </div>
  <dl class="meta">
    <div><dt>Components</dt><dd>{manifest['count']}</dd></div>
    <div><dt>Themes</dt><dd>{len(CONFIG['themes'])}</dd></div>
    <div><dt>Version</dt><dd>{manifest['version']}</dd></div>
    <div><dt>Source</dt><dd><a href="{manifest['repo']}">GitHub</a></dd></div>
  </dl>
</header>

<section class="sec" id="foundation">
  <div data-r>{sec_head(
    "Foundation", "Foun&shy;dation",
    "컴포넌트는 시맨틱 토큰만 참조합니다.",
    "프리미티브를 직접 쓰면 테마 교체가 깨집니다. 색은 헥스로 쓰지 않고 토큰명을 CSS 변수로 선언해 씁니다.")}</div>

  <div data-r style="margin-top:clamp(48px,8vh,88px)">
    <h4>Primitive</h4>
    {swatches()}
  </div>

  <div data-r style="margin-top:56px">
    <h4>Semantic — ELUO 테마가 덮어쓰는 값</h4>
    <div class="tw"><table><thead><tr><td>토큰</td><td>코어</td>
      <td>ELUO 오버라이드</td></tr></thead><tbody>{semantic_table()}</tbody></table></div>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Icons — 만들 때 지키는 것</h4>
    <div class="tw"><table class="iconrule"><tbody>
      <tr><td>출처</td><td>Lucide. 다른 아이콘 세트를 섞지 않습니다</td></tr>
      <tr><td>크기</td><td>32×32 기준, 2의 배수로만 — <code>--size-icon-md</code> 32 · <code>--size-icon-lg</code> 64</td></tr>
      <tr><td>스타일</td><td>채우지 않습니다. <code>fill:none</code> 에 선만 — 버튼처럼 채운 아이콘은 쓰지 않습니다</td></tr>
      <tr><td>선 굵기</td><td><code>--icon-strokewidth</code> 1.2. Lucide 기본값 2 는 무겁습니다</td></tr>
      <tr><td>불투명도</td><td><code>--icon-opacity</code> 0.7. 글자보다 한 단계 물러나야 옆의 문장이 읽힙니다</td></tr>
      <tr><td>색</td><td><code>currentColor</code>. 부모의 색을 따르므로 테마가 바뀌면 함께 바뀝니다</td></tr>
    </tbody></table></div>
    <div class="icons" style="margin-top:20px">
      <div><i data-lucide="search" width="32" height="32"></i><b>32 · search</b></div>
      <div><i data-lucide="check" width="32" height="32"></i><b>32 · check</b></div>
      <div><i data-lucide="settings" width="32" height="32"></i><b>32 · settings</b></div>
      <div><i data-lucide="arrow-right" width="64" height="64"></i><b>64 · arrow-right</b></div>
      <div><i data-lucide="bell" width="64" height="64"></i><b>64 · bell</b></div>
      <div><i data-lucide="layout-grid" width="64" height="64"></i><b>64 · layout-grid</b></div>
    </div>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Typography — 어느 자리에 무엇을 쓰나</h4>
    <p class="note">수치만 있고 역할이 없으면 제목과 본문이 다 비슷한 크기로 나옵니다.
      <code>display1</code>은 한 화면에 하나뿐이고, 위계를 건너뛰지 않습니다.
      크기는 직접 쓰지 말고 <code>var(--type-heading1-size)</code>, 또는 한 줄 축약형
      <code>font:var(--type-heading1)</code>을 씁니다.</p>
    <div class="tw"><table>{type_scale()}</table></div>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Layout — 어디에 얼마나 놓나</h4>
    <p class="note">자산이 아무리 정확해도 폭과 리듬이 없으면 성의 없어 보입니다.
      아래 값은 테마가 덮어씁니다 — 고객사 실측이 있으면 그 값이 정답입니다.
      manifest의 <code>foundationByTheme.&lt;테마&gt;.layout</code>에서 읽으십시오.</p>
    <div class="tw"><table>{layout_table()}</table></div>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Korean — 한글 조판</h4>
    <p class="note">한글은 어절 중간에서 끊기면 읽기가 확 나빠지고, 그렇다고
      <code>keep-all</code>만 걸면 긴 영문 주소가 레이아웃을 밀어냅니다.
      <strong>두 속성을 짝으로 겁니다.</strong> 줄바꿈을 <code>&lt;br&gt;</code>로 넣지 않습니다 —
      폭이 바뀌면 엉뚱한 자리에서 끊깁니다.</p>
    <div class="tw"><table>{text_table()}</table></div>
    <pre class="prompt">/* 본문에 거는 한 벌 */
word-break: var(--text-break);
overflow-wrap: var(--text-overflowWrap);
text-wrap: var(--text-wrap);</pre>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Spacing</h4>
    <p class="note">간격은 임의값을 쓰지 않습니다. 이 눈금 위에서만 고릅니다.</p>
    <div class="tw"><table>{space_table()}</table></div>
  </div>

  <div data-r style="margin-top:56px">
    <h4>Elevation</h4>
    <div class="tw"><table>{elevation_table()}</table></div>
  </div>
</section>

{sections}

<section class="sec" id="agent">
  <div data-r>{sec_head(
    "How to use", "Agents",
    "클로드에게 이 시스템을 쓰게 하는 가장 짧은 형태입니다.",
    "자세한 템플릿은 저장소의 prompts/ 에 있습니다. 자산 ID를 추측하게 두지 말고, 항상 manifest를 먼저 읽히세요.")}</div>
  <div data-r style="margin-top:clamp(48px,8vh,88px)">
    <pre class="prompt">{manifest['repo']} 의 CLAUDE.md 와 manifest.json 을 읽고,
거기 있는 자산으로만 &lt;화면 이름&gt; 시안을 만들어줘.
테마는 {CONFIG['defaultTheme']} 를 쓰고, 쓸 자산 ID 목록을 먼저 보여준 뒤
내 승인을 받고 조립해. spec 값은 바꾸지 마.</pre>
  </div>
</section>

<footer>
  <span>Eluon Design System · {manifest['version']} · 디자인포지션</span>
  <span>이 페이지는 <code>scripts/build_docs.py</code>가 manifest와 레시피에서 생성합니다.</span>
</footer>

</div>

<div class="sendbar" id="sendbar" hidden>
  <span class="sbcount"><b id="sbN">0</b>개 골랐습니다</span>
  <span class="sbids" id="sbIds"></span>
  <button type="button" class="sbclear" id="sbClear">해제</button>
  <a class="sbgo" id="sbGo" href="#">빌더로 보내기</a>
</div>

<button class="totop" id="totop" type="button" aria-label="맨 위로"><i data-lucide="arrow-up"></i></button>

<script>
(function(){{
  var bar=document.getElementById('sendbar');
  function boxes(){{ return Array.prototype.slice.call(document.querySelectorAll('.pickbox')); }}
  function sync(){{
    var ids=boxes().filter(function(b){{return b.checked;}}).map(function(b){{return b.value;}});
    bar.hidden = ids.length===0;
    document.getElementById('sbN').textContent=ids.length;
    document.getElementById('sbIds').textContent=ids.join(', ');
    var th=document.documentElement.getAttribute('data-eluon-theme')||'{CONFIG["defaultTheme"]}';
    document.getElementById('sbGo').href=
      'prompt-builder.html?tab=builder&theme='+encodeURIComponent(th)+
      '&picked='+encodeURIComponent(ids.join(','));
  }}
  boxes().forEach(function(b){{ b.addEventListener('change', sync); }});
  document.getElementById('sbClear').addEventListener('click', function(){{
    boxes().forEach(function(b){{ b.checked=false; }}); sync();
  }});
  sync();
  // 테마를 바꾸면 넘길 주소의 테마도 따라가야 합니다.
  document.querySelectorAll('.themes button').forEach(function(b){{
    b.addEventListener('click', sync);
  }});
}})();

document.querySelectorAll('.themes button').forEach(function(b){{
  b.addEventListener('click', function(){{
    var t = b.dataset.theme;
    document.documentElement.setAttribute('data-eluon-theme', t);
    document.querySelectorAll('.themes button').forEach(function(x){{
      x.setAttribute('aria-pressed', String(x === b));
    }});
    document.getElementById('themeName').textContent = b.textContent;
    document.getElementById('themeHint').textContent = b.dataset.hint || '';
  }});
}});
(function(){{
  var els = document.querySelectorAll('[data-r]');
  if (!('IntersectionObserver' in window)) {{
    els.forEach(function(e){{ e.classList.add('in'); }});
    return;
  }}
  var io = new IntersectionObserver(function(entries){{
    entries.forEach(function(en){{
      if (en.isIntersecting) {{ en.target.classList.add('in'); io.unobserve(en.target); }}
    }});
  }}, {{ rootMargin: '0px 0px -10% 0px', threshold: 0 }});
  els.forEach(function(e){{ io.observe(e); }});
}})();

/* 햄버거 — 좁은 화면에서만 보입니다. */
(function(){{
  var tog = document.getElementById('navtog'), menu = document.getElementById('barmenu');
  function set(open){{
    if (open) menu.setAttribute('data-open',''); else menu.removeAttribute('data-open');
    tog.setAttribute('aria-expanded', String(open));
    tog.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    tog.innerHTML = '<i data-lucide="' + (open ? 'x' : 'menu') + '"></i>';
    if (window.lucide) lucide.createIcons();
  }}
  tog.addEventListener('click', function(){{ set(!menu.hasAttribute('data-open')); }});
  menu.querySelectorAll('nav a').forEach(function(a){{
    a.addEventListener('click', function(){{ set(false); }});
  }});
  document.addEventListener('keydown', function(e){{
    if (e.key === 'Escape' && menu.hasAttribute('data-open')) {{ set(false); tog.focus(); }}
  }});
  window.addEventListener('resize', function(){{
    if (window.innerWidth >= 900 && menu.hasAttribute('data-open')) set(false);
  }});
}})();

/* 맨 위로 */
(function(){{
  var fab = document.getElementById('totop');
  var smooth = !window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  function upd(){{ fab.classList.toggle('on', window.scrollY > 600); }}
  window.addEventListener('scroll', upd, {{ passive: true }});
  upd();
  fab.addEventListener('click', function(){{
    window.scrollTo({{ top: 0, behavior: smooth ? 'smooth' : 'auto' }});
  }});
}})();

if (window.lucide) lucide.createIcons();
</script>
</body></html>
"""
    # 파이프라인 마지막 단계라 여기서는 모든 생성물이 있어야 정상입니다.
    missing = [th for th in CONFIG["themes"]
               if not (ROOT / "index" / f"sheet-{th}.png").exists()]
    if missing:
        print("몽타주 시트가 없습니다 — make_montage.py 를 돌리세요: "
              + ", ".join(f"sheet-{th}.png" for th in missing))
        return 1

    target = ROOT / "docs" / "index.html"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != page:
            print("커밋본이 낡았습니다. build_docs.py 를 다시 돌리세요: docs/index.html")
            return 1
        print("docs/index.html 최신 상태입니다.")
        return 0
    target.write_text(page, encoding="utf-8")
    (ROOT / "docs" / ".nojekyll").write_text("", encoding="utf-8")
    print(f"✓ docs/index.html — 컴포넌트 {len(comps)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
build_guide.py — 사용설명서를 문서 사이트의 한 페이지로 만듭니다.

본문은 docs/guide.src.html 에 사람이 씁니다. 버전과 개수만 여기서 채웁니다 —
설명서가 저장소 밖에 있을 때 매번 어긋나던 자리가 그곳입니다.

설명서는 자산 갤러리와 성격이 다른 문서라 자기 스타일을 그대로 씁니다.
사이트와 이어져 보이도록 상단 바를 같은 모양으로 얹고, 본문이 길어
스크롤로만 찾아야 했던 문제 때문에 왼쪽에 차례를 세웁니다 — 차례는
본문의 <section id> 와 <h3> 에서 자동으로 나오므로 손으로 관리하지 않습니다.

사용:
    python3 scripts/build_guide.py
    python3 scripts/build_guide.py --check   # 커밋본이 낡았으면 실패 (CI용)

산출: docs/guide.html
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))

CHROME_CSS = """
/* ─────────────────────────────────────────────────────────────
   상단 바 · 왼쪽 차례 — build_guide.py 가 얹습니다.
   색과 활자는 본문이 이미 선언한 변수만 씁니다. 새 색을 들이지 않습니다.
   ───────────────────────────────────────────────────────────── */
:root{ --gbar:64px; --gside:264px; --gpad:clamp(20px,5vw,120px) }
@media (max-width:640px){ :root{ --gbar:56px } }

/* 상단 바 — docs/index.html 과 같은 모양. 설명서가 사이트의 일부로 읽히게 합니다. */
.gbar{
  position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:28px;
  height:var(--gbar);padding:0 var(--gpad);
  background:var(--paper);border-bottom:1px solid var(--rule);
}
.gbar .logo{
  font-family:var(--sans);font-size:19px;font-weight:700;letter-spacing:-.04em;
  color:var(--ink);text-decoration:none;
}
.gbar nav{display:flex;gap:22px;margin-left:auto;flex-wrap:wrap}
.gbar nav a{
  font-size:13px;font-weight:700;color:var(--muted);text-decoration:none;
  white-space:nowrap;letter-spacing:-.01em;
}
.gbar nav a:hover{color:var(--ink)}
.gbar nav a[aria-current=page]{color:var(--ink)}
@media (max-width:640px){
  .gbar{gap:16px}
  .gbar nav{gap:14px}
  .gbar nav a{font-size:12px}
}

/* 본문으로 건너뛰기 — 차례가 본문 앞에 오므로 키보드 사용자에게 필요합니다. */
.gskip{
  position:absolute;left:-9999px;top:0;z-index:60;
  padding:10px 16px;background:var(--ink);color:var(--paper);
  font-size:13px;font-weight:700;text-decoration:none;
}
.gskip:focus{left:var(--gpad);top:8px}

/* 두 칼럼 — 프롬프트 빌더의 .shell 과 같은 폭·여백 눈금 */
.gshell{
  width:100%;max-width:1440px;margin-inline:auto;padding-inline:var(--gpad);
  display:grid;grid-template-columns:var(--gside) minmax(0,1fr);gap:40px;
  align-items:start;
}

/* 왼쪽 차례 */
.gside{
  position:sticky;top:var(--gbar);align-self:start;
  max-height:calc(100vh - var(--gbar));overflow-y:auto;overscroll-behavior:contain;
  padding:40px 24px 56px 0;border-right:1px solid var(--hair);
}
.gside::-webkit-scrollbar{width:6px}
.gside::-webkit-scrollbar-thumb{background:var(--hair)}
.gtoggle{display:none}
.gnavttl{
  font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--faint);margin-bottom:14px;
}
.gnav ol{list-style:none}
.gnav > ol > li + li{margin-top:2px}
.gnav .kicker{
  display:block;margin:18px 0 2px;
  font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--faint);
}
.gnav > ol > li:first-child .kicker{margin-top:0}
.gnav a{
  display:block;padding:5px 0;color:var(--muted);text-decoration:none;
  font-size:14px;line-height:21px;letter-spacing:-.2px;
}
.gnav a:hover{color:var(--ink)}
.gnav > ol > li > a[aria-current=true]{color:var(--ink);font-weight:700}
.gnav .sub{display:none;margin:2px 0 4px;padding-left:12px;border-left:1px solid var(--hair)}
.gnav li.is-open > .sub{display:block}
.gnav .sub a{font-size:13px;line-height:20px;padding:4px 0;color:var(--faint)}
.gnav .sub a:hover{color:var(--ink)}
.gnav .sub a[aria-current=true]{color:var(--accent);font-weight:700}

/* 본문 칼럼 — 폭은 이제 셸이 정하므로 .wrap 의 자기 폭을 풉니다. */
.gmain{min-width:0}
.gmain .wrap{max-width:none;margin-inline:0;padding-inline:0}
.gmain header{padding-top:56px}
/* 상단 바에 제목이 가리지 않도록 */
.gmain section,.gmain h3{scroll-margin-top:calc(var(--gbar) + 20px)}

/* 좁은 화면 — 차례를 접어 상단 바 아래 토글로 */
@media (max-width:1023px){
  .gshell{grid-template-columns:minmax(0,1fr);gap:0}
  .gside{
    position:sticky;top:var(--gbar);z-index:30;
    max-height:none;overflow:visible;padding:0;
    border-right:0;border-bottom:1px solid var(--hair);background:var(--paper);
  }
  .gtoggle{
    display:flex;align-items:center;gap:10px;width:100%;
    height:56px;padding:0;border:0;background:none;cursor:pointer;
    font-family:var(--sans);font-size:13px;font-weight:700;color:var(--ink);
    letter-spacing:-.2px;
  }
  /* 아이콘 — CLAUDE.md 규칙: Lucide · 24 기준 · fill 없음 · 굵기 1.2 · 불투명도 .7 */
  .gtoggle [data-lucide]{
    width:var(--size-icon-md,24px);height:var(--size-icon-md,24px);flex:0 0 auto;
    fill:var(--icon-fill,none);stroke:var(--icon-stroke,currentColor);
    stroke-width:var(--icon-strokewidth,1.2);opacity:var(--icon-opacity,.7);
  }
  .gtoggle .caret{margin-left:auto;transition:transform .18s ease}
  .gtoggle[aria-expanded=true] .caret{transform:rotate(180deg)}
  .gnavttl{display:none}   /* 토글 버튼이 이미 "차례"라고 적혀 있습니다 */
  .gtoc{display:none;max-height:min(60vh,420px);overflow-y:auto;padding:4px 0 24px}
  .gside.is-open .gtoc{display:block}
  .gnav li.is-open > .sub{display:block}
  .gmain header{padding-top:40px}
}
@media (prefers-reduced-motion:reduce){ .gtoggle .caret{transition:none} }
"""

CHROME_JS = """
lucide.createIcons();

/* 왼쪽 차례 — 지금 읽는 자리를 표시하고, 그 절의 소제목만 펼칩니다. */
(function () {
  var side   = document.getElementById('gside');
  var toggle = side.querySelector('.gtoggle');
  var links  = Array.prototype.slice.call(document.querySelectorAll('.gnav a'));
  if (!links.length) return;

  var marks = Array.prototype.slice.call(
    document.querySelectorAll('.gmain section[id], .gmain h3[id]'));
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });

  var bar = 0, ticking = false, current = null;
  function measure() {
    bar = parseInt(getComputedStyle(document.documentElement)
            .getPropertyValue('--gbar'), 10) + 24;
  }

  function sync() {
    ticking = false;
    var cur = marks[0];
    for (var i = 0; i < marks.length; i++) {
      if (marks[i].getBoundingClientRect().top <= bar) cur = marks[i];
      else break;
    }
    if (!cur || cur === current) return;
    current = cur;

    links.forEach(function (a) { a.removeAttribute('aria-current'); });
    var here = byId[cur.id];
    if (here) here.setAttribute('aria-current', 'true');

    var sec = cur.tagName === 'SECTION' ? cur : cur.closest('section');
    var secLink = sec && byId[sec.id];
    if (secLink) secLink.setAttribute('aria-current', 'true');

    document.querySelectorAll('.gnav > ol > li').forEach(function (li) {
      li.classList.toggle('is-open', !!sec && li.dataset.sec === sec.id);
    });

    /* 차례가 길어 활성 항목이 시야 밖일 수 있습니다 */
    if (here && window.matchMedia('(min-width:1024px)').matches) {
      var r = here.getBoundingClientRect(), s = side.getBoundingClientRect();
      if (r.top < s.top + 8 || r.bottom > s.bottom - 8) {
        here.scrollIntoView({ block: 'nearest' });
      }
    }
  }

  function onScroll() {
    if (!ticking) { ticking = true; requestAnimationFrame(sync); }
  }

  measure();
  sync();
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', function () { measure(); current = null; sync(); });

  toggle.addEventListener('click', function () {
    var open = side.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  links.forEach(function (a) {
    a.addEventListener('click', function () {
      side.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
})();
"""

TAG_RE = re.compile(r'<span class="tag">.*?</span>', re.S)


def values(manifest):
    groups = len({a["group"] for a in manifest["assets"] if not a.get("variantOf")})
    varying = sum(
        1 for a in manifest["assets"]
        if not a.get("variantOf")
        and len({json.dumps(v, sort_keys=True) for v in a["specByTheme"].values()}) > 1)
    return {
        "version": manifest["version"],
        "count": str(manifest["count"]),
        "variants": str(manifest.get("variantCount", 0)),
        "themes": str(len(manifest["themes"])),
        "groups": str(groups),
        "varying": str(varying),
    }


def fill(body, vals):
    """{{name}} 을 채웁니다. 모르는 이름이 남아 있으면 실패시킵니다 —
    조용히 그대로 나가면 독자가 자리표시자를 값으로 읽습니다."""
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: vals.get(m.group(1), m.group(0)), body)
    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", out)))
    return out, left


def flat(fragment):
    """차례에 넣을 글자만 남깁니다. 버전 꼬리표는 제목이 아니라 표식이라 뺍니다."""
    text = re.sub(r"<[^>]+>", "", TAG_RE.sub("", fragment))
    return html.escape(re.sub(r"\s+", " ", html.unescape(text)).strip())


def outline(body):
    """<section id> 를 훑어 차례를 만들고, 소제목에 id 를 붙여 돌려줍니다.

    id 없는 절은 차례에서 조용히 빠지므로 실패시킵니다 — 목차에 없는 절은
    독자에게 없는 절입니다."""
    secs, missing = [], []

    def one(m):
        attrs, inner = m.group(1), m.group(2)
        found = re.search(r'id="([^"]+)"', attrs)
        if not found:
            head = re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.S)
            missing.append(flat(head.group(1)) if head else "(제목 없는 절)")
            return m.group(0)
        sid = found.group(1)

        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', inner, re.S)
        title = re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.S)
        subs = []

        def number(sub):
            subs.append((f"{sid}-{len(subs) + 1}", flat(sub.group(1))))
            return f'<h3 id="{subs[-1][0]}">{sub.group(1)}</h3>'

        inner = re.sub(r"<h3>(.*?)</h3>", number, inner, flags=re.S)
        secs.append({
            "id": sid,
            "kicker": flat(eyebrow.group(1)) if eyebrow else "",
            "title": flat(title.group(1)) if title else sid,
            "subs": subs,
        })
        return f"<section{attrs}>{inner}</section>"

    body = re.sub(r"<section([^>]*)>(.*?)</section>", one, body, flags=re.S)
    return body, secs, missing


def nav_html(secs):
    rows = []
    for s in secs:
        sub = ""
        if s["subs"]:
            items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in s["subs"])
            sub = f'\n        <ol class="sub">{items}</ol>'
        kicker = f'<span class="kicker">{s["kicker"]}</span>' if s["kicker"] else ""
        rows.append(
            f'      <li data-sec="{s["id"]}">{kicker}'
            f'<a href="#{s["id"]}">{s["title"]}</a>{sub}</li>')
    return ('<nav class="gnav" aria-label="차례">\n'
            '    <p class="gnavttl">차례</p>\n'
            '    <ol>\n' + "\n".join(rows) + "\n    </ol>\n  </nav>")


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    src = (ROOT / "docs" / "guide.src.html").read_text(encoding="utf-8")
    body = re.sub(r"^<!--.*?-->\n", "", src, count=1, flags=re.S)

    vals = values(manifest)
    body, left = fill(body, vals)
    if left:
        print("채우지 못한 자리표시자: " + ", ".join("{{%s}}" % x for x in left))
        return 1

    # 본문의 <style> 은 머리로 올리고, 그 뒤에 상단 바·차례 스타일을 덧붙입니다.
    split = re.match(r"\s*(<style>.*?</style>)(.*)$", body, re.S)
    if not split:
        print("guide.src.html 이 <style> 로 시작하지 않습니다")
        return 1
    style = split.group(1).replace("</style>", CHROME_CSS + "</style>", 1)
    content = split.group(2)

    content, secs, missing = outline(content)
    if missing:
        print("id 가 없는 절: " + ", ".join(missing))
        print('차례에 실리려면 <section id="..."> 로 적어야 합니다.')
        return 1
    if not secs:
        print("절을 하나도 찾지 못했습니다")
        return 1

    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eluon — 사용설명서</title>
<meta name="description" content="Eluon 디자인 시스템 사용설명서. {vals['version']} 기준.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap">
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
{style}
</head>
<body>

<a class="gskip" href="#gmain">본문으로 건너뛰기</a>

<div class="gbar">
  <a class="logo" href="index.html">eluon</a>
  <nav>
    <a href="index.html">디자인 시스템</a>
    <a href="prompt-builder.html">프롬프트 빌더</a>
    <a href="guide.html" aria-current="page">사용설명서</a>
  </nav>
</div>

<div class="gshell">
  <aside class="gside" id="gside">
    <button class="gtoggle" type="button" aria-expanded="false" aria-controls="gtoc">
      <i data-lucide="list"></i><span>차례</span>
      <i class="caret" data-lucide="chevron-down"></i>
    </button>
    <div class="gtoc" id="gtoc">
  {nav_html(secs)}
    </div>
  </aside>

  <div class="gmain" id="gmain">
{content}
  </div>
</div>

<script>{CHROME_JS}</script>
</body>
</html>
"""
    target = ROOT / "docs" / "guide.html"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != page:
            print("커밋본이 낡았습니다. build_guide.py 를 다시 돌리세요: docs/guide.html")
            return 1
        print("docs/guide.html 최신 상태입니다.")
        return 0
    target.write_text(page, encoding="utf-8")
    subs = sum(len(s["subs"]) for s in secs)
    print(f"✓ docs/guide.html — {vals['version']} · 자산 {vals['count']}개 "
          f"· 차례 {len(secs)}절 / 소제목 {subs}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())

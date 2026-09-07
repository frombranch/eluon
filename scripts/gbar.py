#!/usr/bin/env python3
"""
gbar.py — 사이트 공통 상단 내비게이션(GNB).

세 페이지가 저마다 다른 상단 바를 갖고 있었습니다. 정본을 여기 한 곳에 두고
셋이 같은 것을 씁니다. 기준은 **사용설명서**의 모양입니다. (2026-09-07 통일)

  build_docs.py   → docs/index.html          (디자인 시스템)
  build_guide.py  → docs/guide.html          (사용설명서)
  docs/prompt-builder.html                    (프롬프트 빌더)

빌더는 손으로 쓰는 파일이라 같은 CSS·마크업을 그대로 베껴 두었습니다.
여기를 고치면 빌더도 함께 고칩니다 — 파일 안에 그 표시를 남겨 두었습니다.

색과 활자는 각 페이지가 이미 선언한 변수만 씁니다. 새 색을 들이지 않습니다.
페이지마다 변수 이름이 달라서, 이름이 없는 쪽은 :root 에 별칭을 답니다.

  --paper  바탕      --ink   글자
  --rule   경계선    --muted 흐린 글자

활자와 행간은 바가 직접 정합니다(--gfont · line-height:1). 페이지마다 본문 글꼴과
행간이 달라서, 상속받으면 로고와 링크의 자리가 몇 px 씩 어긋납니다.
"""

# 상단 바 높이는 다른 sticky 요소가 기준으로 삼습니다(설명서의 차례 등).
# 그래서 값이 아니라 변수로 나갑니다.
GBAR_CSS = """
/* ── 상단 내비게이션 — scripts/gbar.py 가 정본입니다 ────────────────
   세 페이지(디자인 시스템 · 프롬프트 빌더 · 사용설명서)가 같은 것을 씁니다.
   여기만 고쳐서는 안 됩니다. gbar.py 를 고치고 세 곳을 함께 내보냅니다.
   ──────────────────────────────────────────────────────────────── */
/* 글꼴을 바가 직접 정합니다. 페이지의 --sans 를 따르면 설명서만 Noto Sans KR 이라
   같은 글자의 폭이 달라지고, 오른쪽 링크 줄이 페이지마다 어긋납니다.
   설명서에도 이 글꼴을 실어 두었습니다(build_guide.py). 본문은 그대로 둡니다. */
:root{
  --gbar:64px; --gpad:clamp(20px,5vw,120px);
  --gfont:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo",sans-serif;
}
@media (max-width:640px){ :root{ --gbar:56px } }

/* 여백은 화면 기준입니다. 페이지마다 본문 폭 규칙이 달라서(빌더·설명서는 1440 에서 멈추고
   디자인 시스템은 레일이 화면 끝에 붙습니다) 본문에 맞추면 바가 서로 어긋납니다.
   바끼리 같은 자리에 서는 것을 먼저 둡니다. */
.gbar{
  position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:28px;
  height:var(--gbar);padding:0 var(--gpad);
  background:var(--paper);border-bottom:1px solid var(--rule);
}
/* line-height 를 못박습니다 — 본문 행간(페이지마다 1.5~1.65)이 상속되면
   글자 상자 높이가 달라져 세로 중심이 페이지마다 몇 px 씩 어긋납니다. */
.gbar .logo{
  font-family:var(--gfont);font-size:19px;font-weight:700;letter-spacing:-.04em;
  line-height:1;color:var(--ink);text-decoration:none;
}
.gbar nav{display:flex;gap:22px;margin-left:auto;flex-wrap:wrap}
.gbar nav a{
  font-family:var(--gfont);font-size:13px;font-weight:700;line-height:1;
  color:var(--muted);text-decoration:none;white-space:nowrap;letter-spacing:-.01em;
}
.gbar nav a:hover{color:var(--ink)}
.gbar nav a[aria-current=page]{color:var(--ink)}
@media (max-width:640px){
  .gbar{gap:16px}
  .gbar nav{gap:14px}
  .gbar nav a{font-size:12px}
}
"""

PAGES = (
    ("index.html", "디자인 시스템"),
    ("prompt-builder.html", "프롬프트 빌더"),
    ("guide.html", "사용설명서"),
)


def gbar_html(current: str) -> str:
    """current 는 지금 페이지의 파일 이름 — 그 링크에만 aria-current 가 붙습니다."""
    links = "".join(
        '\n    <a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if href == current else "", label)
        for href, label in PAGES
    )
    return (
        '<div class="gbar">\n'
        '  <a class="logo" href="index.html">Eluon</a>\n'
        '  <nav aria-label="사이트 이동">%s\n'
        "  </nav>\n"
        "</div>" % links
    )

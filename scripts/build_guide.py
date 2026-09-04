#!/usr/bin/env python3
"""
build_guide.py — 사용설명서를 문서 사이트의 한 페이지로 만듭니다.

본문은 docs/guide.src.html 에 사람이 씁니다. 버전과 개수만 여기서 채웁니다 —
설명서가 저장소 밖에 있을 때 매번 어긋나던 자리가 그곳입니다.

설명서는 자산 갤러리와 성격이 다른 문서라 자기 스타일을 그대로 씁니다.
사이트와 이어져 보이도록 상단 바만 같은 모양으로 얹습니다.

사용:
    python3 scripts/build_guide.py
    python3 scripts/build_guide.py --check   # 커밋본이 낡았으면 실패 (CI용)

산출: docs/guide.html
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))

BAR_CSS = """
/* 상단 바 — docs/index.html 과 같은 모양. 설명서가 사이트의 일부로 읽히게 합니다. */
.gbar{
  position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:28px;
  height:64px;padding:0 clamp(20px,5vw,120px);
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
  .gbar{gap:16px;height:56px}
  .gbar nav{gap:14px}
  .gbar nav a{font-size:12px}
}
"""


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


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    src = (ROOT / "docs" / "guide.src.html").read_text(encoding="utf-8")
    body = re.sub(r"^<!--.*?-->\n", "", src, count=1, flags=re.S)

    vals = values(manifest)
    body, left = fill(body, vals)
    if left:
        print("채우지 못한 자리표시자: " + ", ".join("{{%s}}" % x for x in left))
        return 1

    # 본문의 <style> 뒤에 상단 바 스타일을 덧붙입니다.
    if "</style>" not in body:
        print("guide.src.html 에 <style> 이 없습니다")
        return 1
    body = body.replace("</style>", BAR_CSS + "</style>", 1)

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
</head>
<body>

<div class="gbar">
  <a class="logo" href="index.html">eluon</a>
  <nav>
    <a href="index.html">디자인 시스템</a>
    <a href="prompt-builder.html">프롬프트 빌더</a>
    <a href="guide.html" aria-current="page">사용설명서</a>
  </nav>
</div>

{body}
<script>lucide.createIcons();</script>
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
    print(f"✓ docs/guide.html — {vals['version']} · 자산 {vals['count']}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())

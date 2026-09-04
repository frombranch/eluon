#!/usr/bin/env python3
"""
build_measure.py — 테마마다 무엇을 더 받아야 하는지 표로 만듭니다.

"atlas 는 25축 중 1축만 실측" 같은 상태를 사람이 파악할 방법이 없었습니다.
$measured 는 산문이라 읽어야 알고, 안 적힌 축은 아예 보이지 않습니다.
이 스크립트는 core 의 축 목록과 테마가 실제로 덮어쓴 것을 대조해,
빠진 축을 그대로 나열합니다.

고객사명은 들어가지 않습니다 — 가명과 축 이름뿐이라 공개 저장소에 둡니다.

산출: index/MEASURE.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_pb_manifest import SIZE_GROUP_KO, THEME_KO

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
CORE = json.loads((ROOT / "tokens" / "core.json").read_text(encoding="utf-8"))

STATUS_KO = {
    "measured":  ("실측", "색·치수 모두 실측입니다."),
    "partial":   ("일부 실측", "색은 실측이고 치수는 일부만 옮겼습니다."),
    "estimated": ("추정", "⚠ 색부터 추정입니다. 대외 제출물에 쓰지 마십시오."),
}

# 축 하나를 채우려면 무엇을 받아야 하는지. 요청서에 그대로 씁니다.
ASK = {
    "control":    "버튼 3단(대·중·소)의 높이와 좌우 패딩",
    "field":      "입력 필드 높이·좌우 패딩·폭",
    "card":       "카드 폭·패딩·내부 간격·썸네일 비율",
    "table":      "표의 행 높이·헤더 높이·좌우 패딩",
    "modal":      "모달 폭·패딩·내부 간격",
    "toast":      "토스트 폭·패딩·내부 간격",
    "tab":        "탭 높이·항목 간격·밑줄 두께",
    "pagination": "페이지네이션 항목 크기·간격",
    "chip":       "칩 높이·좌우 패딩",
    "badge":      "배지 높이·좌우 패딩",
    "toggle":     "토글 크기·아이콘 크기",
    "section":    "섹션 머리의 요소 간 간격",
    "price":      "가격 표기의 요소 간 간격",
    "border":     "테두리 두께 (rem 인지 고정 px 인지 함께)",
    "focusRing":  "포커스 링 두께",
    "header":     "상단 헤더 높이·메뉴 간격",
    "hero":       "첫 화면의 칼럼 간격·액션 간격",
    "footer":     "하단 푸터 상하 여백·요소 간격",
    "ctaBand":    "전환 유도 띠의 상하 여백",
    "listRow":    "목록 한 줄의 상하 여백·요소 간격",
    "accordion":  "아코디언 항목의 상하 여백·아이콘 크기",
    "breadcrumb": "경로 항목 간격·항목 최대 폭",
    "empty":      "빈 상태의 상하 여백·본문 최대 폭",
    "descList":   "정의 목록의 라벨 폭·행 여백",
    "stepFlow":   "절차 번호 크기·단계 간 간격",
}


def axes():
    return sorted({k.split(".")[0] for k in CORE["semantic"]["size"]})


def theme_rows(th):
    d = json.loads((ROOT / "tokens" / f"theme-{th}.json").read_text(encoding="utf-8"))
    sem = d.get("semantic", {})
    got = {k.split(".")[0] for k in (sem.get("size") or {})}
    return d, got, [a for a in axes() if a not in got]


def main() -> int:
    ko = lambda a: SIZE_GROUP_KO.get(a, a)
    total = len(axes())
    out = [
        "# 테마 실측 현황", "",
        f"`{CONFIG['version']}` · 치수 축 {total}개 기준", "",
        "> `scripts/build_measure.py`가 생성합니다. 직접 고치지 마세요.",
        "> 고객사명은 들어가지 않습니다. 어느 고객사인지는 private 노트를 보십시오.", "",
        "| 테마 | 상태 | 치수 | 색 | 라운드 | 레이아웃 | 활자 | 폰트 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    detail = []
    for th in CONFIG["themes"]:
        d, got, miss = theme_rows(th)
        sem = d.get("semantic", {})
        is_default = th == CONFIG["defaultTheme"]
        status = "measured" if is_default else d.get("$status", "?")
        label = STATUS_KO.get(status, (status, ""))[0]
        mark = lambda x: "O" if x else "—"
        # 자사 테마는 core 가 곧 우리 값이라 "0/25" 로 적으면 안 잰 것처럼 읽힙니다.
        size_cell = "기본값이 정답" if is_default else f"{len(got)}/{total}"
        out.append(
            f"| `{th}` {THEME_KO.get(th, ('', ''))[0]} | {label} | "
            f"{size_cell} | {mark(sem.get('color'))} | {mark(sem.get('radius'))} | "
            f"{mark(sem.get('layout'))} | {mark(d.get('typography'))} | {mark(sem.get('font'))} |")
        if is_default:
            continue

        detail += [f"## `{th}` {THEME_KO.get(th, ('', ''))[0]}", "",
                   f"**{label}** — {STATUS_KO.get(status, ('', ''))[1]}", ""]
        m = d.get("$measured") or {}
        for k in ("출처", "환산", "옮긴 것", "안 옮긴 것", "주의"):
            if m.get(k):
                detail.append(f"- **{k}** {m[k]}")
        detail.append("")
        if miss:
            detail += [f"### 더 받아야 하는 것 — 치수 {len(miss)}축", ""]
            # 한글 이름 순으로 읽는 사람이 찾기 쉽게 정렬합니다.
            detail += [f"- [ ] **{ko(a)}** — {ASK.get(a, a)}"
                       for a in sorted(miss, key=ko)]
            detail.append("")
        need = []
        if not sem.get("layout"):
            need.append("**레이아웃** — 콘텐츠 최대폭·좌우 거터·그리드 열·섹션 상하 여백")
        if not d.get("typography"):
            need.append("**활자** — 제목·본문 단계별 크기·굵기·자간·행간")
        if not sem.get("font"):
            need.append("**폰트** — 본문 서체 이름과 웹폰트 제공 여부")
        if need:
            detail += ["### 더 받아야 하는 것 — 치수 밖", ""] + [f"- [ ] {n}" for n in need] + [""]

    text = "\n".join(out + [""] + detail) + "\n"
    (ROOT / "index").mkdir(exist_ok=True)
    (ROOT / "index" / "MEASURE.md").write_text(text, encoding="utf-8")
    print(f"✓ index/MEASURE.md — 테마 {len(CONFIG['themes'])}종")
    return 0


if __name__ == "__main__":
    sys.exit(main())

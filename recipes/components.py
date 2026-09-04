# -*- coding: utf-8 -*-
"""
Eluon 컴포넌트 레시피.

여기 적힌 spec 수치가 그대로 CSS에 들어가고, 그 CSS가 그대로 PNG로 렌더됩니다.
즉 manifest의 spec과 실제 이미지가 어긋날 수 없습니다 — 같은 곳에서 나오기 때문입니다.
컴포넌트를 추가하려면 이 파일에 dict 하나를 더합니다.

규칙
  - 색은 반드시 var(--color-*) 시맨틱 토큰으로. 헥스 직접 사용 금지.
  - 라운드는 var(--radius-*). 테마마다 값이 다릅니다.
  - 크기·간격도 var(--size-*) 토큰으로. 숫자를 직접 쓰지 않습니다.
    spec에는 토큰 이름을 적습니다 — 실제 px는 테마가 정합니다.
    고객사마다 버튼 높이·패딩·카드 폭이 다르기 때문입니다. (D-029)
"""

# ── 반응형 규칙 ────────────────────────────────────────────────────────
# 자산이 좁은 폭에서 어떻게 접히는지. 브레이크포인트 이름(sm·md·lg)은
# semantic.breakpoint 에서 오고 실제 px 는 테마가 정합니다.
#
#   fill     폭을 100% 로. 고정폭(320·360·420·520)이 넘치는 것을 막습니다.
#   toCard   표를 카드 목록으로 전환. 열이 3개 넘으면 가로 스크롤보다 낫습니다.
#   scrollX  컨테이너를 가로 스크롤로. 순서가 의미 있는 것(탭·페이지네이션)에.
#   stack    가로로 놓인 칼럼을 세로로 쌓음. 히어로·푸터·CTA 띠·목록 행.
#   menuNav  가로 메뉴를 접고 토글 버튼 하나로. 헤더 전용.
#   (없음)   폭이 hug 라 그대로 둬도 됩니다.
#
# 한 곳에 모아 둔 이유: 화면마다 다르게 접히면 시스템이 아닙니다.
# 여기가 비어 있는 자산은 "좁은 폭에서 그대로 둔다" 는 뜻입니다.
RESPONSIVE = {
    # 고정폭 → 전폭
    "card-basic-md":       {"md": "fill"},
    "card-stat-md":        {"md": "fill"},
    "card-portrait-md":    {"md": "fill"},
    "card-product-md":     {"md": "fill"},
    "input-text-md":       {"md": "fill"},
    "input-text-md-focus": {"md": "fill"},
    "input-text-md-error": {"md": "fill"},
    "select-md":           {"md": "fill"},
    "toast-info-md":       {"sm": "fill"},
    "toast-error-md":      {"sm": "fill"},
    "modal-confirm-lg":    {"sm": "fill"},
    # 주요 CTA 는 모바일에서 전폭이 관례. md·sm 버튼은 그대로 둡니다.
    "btn-primary-lg":      {"sm": "fill"},
    "btn-secondary-lg":    {"sm": "fill"},
    "btn-outline-lg":      {"sm": "fill"},
    "btn-primary-lg-disabled": {"sm": "fill"},
    # 순서가 의미 있는 것 → 가로 스크롤
    "tab-underline-md":    {"md": "scrollX"},
    "pagination-md":       {"sm": "scrollX"},
    # 표는 카드로
    "table-basic-lg":      {"md": "toCard"},
    # 가로 칼럼 → 세로로 쌓기
    "hero-split-lg":       {"md": "stack"},
    "footer-lg":           {"md": "stack"},
    "cta-band-lg":         {"md": "stack"},
    "list-row-md":         {"sm": "stack"},
    "form-field-md":       {"md": "fill"},
    # 헤더 메뉴는 접습니다
    "header-gnb-lg":       {"md": "menuNav"},
    # 라벨과 값이 나란히 있으면 좁은 폭에서 값이 두 글자씩 끊깁니다
    "desc-list-md":        {"sm": "stack"},
}

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;-webkit-font-smoothing:antialiased;
     font-family:var(--font-family-base);color:var(--color-text-primary)}
.stage{display:inline-block}
"""


def t(typ, tokens):
    """타이포 토큰을 CSS 선언으로 펼칩니다."""
    d = tokens["typography"][typ]
    return (f"font-size:{d['size']}px;font-weight:{d['weight']};"
            f"line-height:{d['lineHeight']};letter-spacing:{d['tracking']};")


def sz(name):
    """크기 토큰을 CSS 값으로. 'control.lg.height' → var(--size-control-lg-height)"""
    return f"var(--size-{name.replace('.', '-')})"


KO = ("word-break:var(--text-break);overflow-wrap:var(--text-overflowWrap);"
      "text-wrap:var(--text-wrap);")
"""한글 조판 한 벌.

keep-all 만 두면 긴 영문·URL 이 컨테이너를 넘칩니다. overflow-wrap:anywhere 를
같이 걸어야 한글은 어절째 남고 긴 라틴 문자열만 끊깁니다. 둘은 항상 짝입니다.
text-wrap:pretty 는 마지막 줄에 한 어절만 남는 것을 줄입니다."""

NUM = "font-variant-numeric:var(--text-numeric);"


def lay(name):
    """레이아웃 토큰을 CSS 값으로. 'container.max' → var(--layout-container-max)

    페이지를 이루는 덩어리(헤더·히어로·푸터·CTA 띠)는 콘텐츠 폭 자체가 규격이라
    개별 크기 토큰이 아니라 레이아웃 토큰을 봅니다."""
    return f"var(--layout-{name.replace('.', '-')})"


def build(tokens):
    """토큰을 받아 컴포넌트 정의 리스트를 만듭니다."""
    C = []

    def add(**kw):
        C.append(kw)

    # ── button ──────────────────────────────────────────────────────────
    btn_base = ("display:inline-flex;align-items:center;justify-content:center;"
                "border:0;cursor:pointer;white-space:nowrap;font-family:inherit;")

    for size, rad, typ in [("lg", "lg", "body1-bold"),
                           ("md", "md", "body2-bold"),
                           ("sm", "sm", "label")]:
        add(
            id=f"btn-primary-{size}", name=f"Primary Button / {size.upper()}", group="button",
            tags=["CTA", "주요액션", "채움형"],
            spec={"width": "hug", "height": f"control.{size}.height", "radius": rad,
                  "paddingX": f"control.{size}.paddingX", "typography": typ},
            tokens={"bg": "brand.primary", "label": "text.inverse"},
            states=["default", "hover", "pressed", "disabled"],
            usage={"lg": "화면당 주요 액션 1개. 히어로·폼 제출·전환 유도",
                   "md": "본문 안 액션. 카드 내부나 테이블 행 액션",
                   "sm": "밀도 높은 영역. 툴바·필터 바"}[size],
            dont="삭제·탈퇴 등 파괴적 액션에는 사용 금지 (btn-danger-md 사용)",
            css=f".c{{{btn_base}height:{sz(f'control.{size}.height')};"
                f"padding:0 {sz(f'control.{size}.paddingX')};"
                f"border-radius:var(--radius-{rad});background:var(--color-brand-primary);"
                f"color:var(--color-text-inverse);{t(typ, tokens)}}}",
            html='<button class="c">주요 액션</button>',
        )

    add(
        id="btn-secondary-lg", name="Secondary Button / LG", group="button",
        tags=["보조액션", "외곽선형"],
        spec={"width": "hug", "height": "control.lg.height", "radius": "lg",
              "paddingX": "control.lg.paddingX", "borderWidth": "border.width",
              "typography": "body1-bold"},
        tokens={"border": "border.default", "label": "text.primary", "bg": "surface.default"},
        states=["default", "hover", "pressed", "disabled"],
        usage="주요 액션과 나란히 놓는 두 번째 선택지",
        dont="단독으로 쓰지 않음. 항상 primary와 짝",
        css=f".c{{{btn_base}height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-primary);{t('body1-bold', tokens)}}}",
        html='<button class="c">보조 액션</button>',
    )

    add(
        id="btn-ghost-md", name="Ghost Button / MD", group="button",
        tags=["텍스트버튼", "3순위"],
        spec={"width": "hug", "height": "control.md.height", "radius": "md",
              "paddingX": "control.ghost.paddingX", "typography": "body2-bold"},
        tokens={"label": "text.brand"},
        states=["default", "hover", "disabled"],
        usage="세 번째 순위 액션. 취소·더보기·되돌리기",
        dont="한 화면에 3개 이상 늘어놓지 않음. 위계가 사라짐",
        css=f".c{{{btn_base}height:{sz('control.md.height')};"
            f"padding:0 {sz('control.ghost.paddingX')};border-radius:var(--radius-md);"
            f"background:transparent;color:var(--color-text-brand);{t('body2-bold', tokens)}}}",
        html='<button class="c">더 보기</button>',
    )

    add(
        id="btn-danger-md", name="Danger Button / MD", group="button",
        tags=["파괴적액션", "삭제", "경고"],
        spec={"width": "hug", "height": "control.md.height", "radius": "md",
              "paddingX": "control.md.paddingX", "typography": "body2-bold"},
        tokens={"bg": "danger.default", "label": "text.inverse"},
        states=["default", "hover", "pressed", "disabled"],
        usage="되돌릴 수 없는 액션. 삭제·탈퇴·영구 해제",
        dont="확인 모달 없이 단독 노출 금지",
        css=f".c{{{btn_base}height:{sz('control.md.height')};"
            f"padding:0 {sz('control.md.paddingX')};border-radius:var(--radius-md);"
            f"background:var(--color-danger-default);color:var(--color-text-inverse);"
            f"{t('body2-bold', tokens)}}}",
        html='<button class="c">삭제하기</button>',
    )

    add(
        id="btn-primary-lg-disabled", variantOf="btn-primary-lg", variantState="disabled", name="Primary Button / LG / Disabled", group="button",
        tags=["비활성", "disabled"],
        spec={"width": "hug", "height": "control.lg.height", "radius": "lg",
              "paddingX": "control.lg.paddingX", "typography": "body1-bold"},
        tokens={"bg": "surface.disabled", "label": "text.disabled"},
        usage="필수 입력이 채워지지 않았을 때. 버튼을 감추는 대신 사용",
        dont="이유 안내 없이 단독 노출 금지. 항상 헬퍼 텍스트와 함께",
        css=f".c{{{btn_base}height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"background:var(--color-surface-disabled);color:var(--color-text-disabled);"
            f"cursor:not-allowed;{t('body1-bold', tokens)}}}",
        html='<button class="c" disabled>주요 액션</button>',
    )

    # ── chip ────────────────────────────────────────────────────────────
    chip_base = (f"display:inline-flex;align-items:center;gap:{sz('chip.gap')};"
                 f"height:{sz('chip.height')};padding:0 {sz('chip.paddingX')};"
                 f"border-radius:var(--radius-full);cursor:pointer;")
    add(
        id="chip-filter-md", name="Filter Chip / MD", group="chip",
        tags=["필터", "선택", "토글"],
        spec={"width": "hug", "height": "chip.height", "radius": "full",
              "paddingX": "chip.paddingX", "borderWidth": "border.width",
              "gap": "chip.gap", "typography": "label"},
        tokens={"border": "border.default", "label": "text.secondary", "bg": "surface.default"},
        states=["default", "selected", "disabled"],
        usage="목록 상단의 다중 필터. 2~8개까지",
        dont="단일 선택에는 쓰지 않음. 그건 탭이나 셀렉트",
        css=f".c{{{chip_base}background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-secondary);"
            f"{t('label', tokens)}}}",
        html='<div class="c">진행중</div>',
    )
    add(
        id="chip-filter-md-selected", variantOf="chip-filter-md", variantState="selected", name="Filter Chip / MD / Selected", group="chip",
        tags=["필터", "선택됨"],
        spec={"width": "hug", "height": "chip.height", "radius": "full",
              "paddingX": "chip.paddingX", "borderWidth": "border.width",
              "gap": "chip.gap", "typography": "label"},
        tokens={"bg": "brand.subtle", "border": "border.brand", "label": "brand.onSubtle"},
        usage="선택된 필터. 배경 채움 + 브랜드 테두리로 상태를 이중 표기",
        dont="색만으로 선택을 표시하지 않음. 색각 이상 사용자가 구분 못 함",
        css=f".c{{{chip_base}background:var(--color-brand-subtle);"
            f"border:{sz('border.width')} solid var(--color-border-brand);"
            f"color:var(--color-brand-onSubtle);"
            f"{t('label', tokens)}}}",
        html='<div class="c">✓ 진행중</div>',
    )

    # ── input ───────────────────────────────────────────────────────────
    inp = (f"display:flex;align-items:center;width:{sz('field.width')};"
           f"height:{sz('field.height')};padding:0 {sz('field.paddingX')};"
           f"border-radius:var(--radius-md);background:var(--color-surface-default);")
    add(
        id="input-text-md", name="Text Field / MD", group="input",
        tags=["폼", "텍스트필드"],
        spec={"width": "field.width", "height": "field.height", "radius": "md",
              "paddingX": "field.paddingX", "borderWidth": "border.width",
              "typography": "body2"},
        tokens={"border": "border.default", "placeholder": "text.tertiary"},
        states=["default", "focus", "error", "disabled"],
        usage="한 줄 입력의 기본형",
        dont="라벨 없이 placeholder만으로 쓰지 않음",
        css=f".c{{{inp}border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-tertiary);{t('body2', tokens)}}}",
        html='<div class="c">입력해 주세요</div>',
    )
    add(
        id="input-text-md-focus", variantOf="input-text-md", variantState="focus", name="Text Field / MD / Focus", group="input",
        tags=["폼", "포커스", "접근성"],
        spec={"width": "field.width", "height": "field.height", "radius": "md",
              "paddingX": "field.paddingX", "borderWidth": "border.width",
              "focusRingWidth": "focusRing.width", "typography": "body2"},
        tokens={"border": "border.brand", "ring": "focusRing"},
        usage="키보드 포커스 상태. 링은 테두리 바깥 3px",
        dont="outline:none으로 링을 지우지 않음. 키보드 사용자가 위치를 잃음",
        css=f".c{{{inp}border:{sz('border.width')} solid var(--color-border-brand);"
            f"box-shadow:0 0 0 {sz('focusRing.width')} "
            f"color-mix(in srgb, var(--color-focusRing) 24%, transparent);"
            f"color:var(--color-text-primary);{t('body2', tokens)}}}",
        html='<div class="c">홍길동</div>',
    )
    add(
        id="input-text-md-error", variantOf="input-text-md", variantState="error", name="Text Field / MD / Error", group="input",
        tags=["폼", "에러", "유효성"],
        spec={"width": "field.width", "height": "field.height", "radius": "md",
              "paddingX": "field.paddingX", "borderWidth": "border.width",
              "gap": "field.gap", "typography": "body2"},
        tokens={"border": "border.danger", "helper": "danger.text"},
        usage="유효성 검사 실패. 아래 헬퍼 텍스트로 무엇을 고칠지 함께 안내",
        dont="빨간 테두리만 주고 이유를 적지 않는 것 금지",
        css=f".c{{display:flex;flex-direction:column;gap:{sz('field.gap')};"
            f"width:{sz('field.width')}}}"
            f".f{{{inp}border:{sz('border.width')} solid var(--color-border-danger);"
            f"color:var(--color-text-primary);{t('body2', tokens)}}}"
            f".h{{color:var(--color-danger-text);{t('caption', tokens)}}}",
        html='<div class="c"><div class="f">hong@</div>'
             '<div class="h">이메일 형식이 올바르지 않습니다</div></div>',
    )
    add(
        id="select-md", name="Select / MD", group="input",
        tags=["폼", "드롭다운", "단일선택"],
        spec={"width": "field.width", "height": "field.height", "radius": "md",
              "paddingX": "field.paddingX", "borderWidth": "border.width",
              "typography": "body2"},
        tokens={"border": "border.default", "label": "text.primary", "icon": "text.tertiary"},
        states=["default", "open", "disabled"],
        usage="선택지 6개 이상의 단일 선택",
        dont="선택지 5개 이하면 탭이나 라디오가 더 빠름",
        css=f".c{{{inp}justify-content:space-between;"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-primary);{t('body2', tokens)}}}"
            f".i{{color:var(--color-text-tertiary);font-size:12px}}",
        html='<div class="c"><span>서울특별시</span><span class="i">▼</span></div>',
    )

    # ── card ────────────────────────────────────────────────────────────
    add(
        id="card-basic-md", name="Basic Card / MD", group="card",
        tags=["카드", "컨테이너"],
        spec={"width": "card.width", "radius": "xl", "paddingX": "card.basic.paddingX",
              "paddingY": "card.basic.paddingY", "gap": "card.basic.gap",
              "borderWidth": "border.width", "elevation": 1},
        tokens={"bg": "surface.default", "border": "border.subtle"},
        states=["default", "hover"],
        usage="구획을 나누는 기본 컨테이너",
        dont="카드 안에 또 카드를 넣지 않음",
        css=f".c{{width:{sz('card.width')};"
            f"padding:{sz('card.basic.paddingY')} {sz('card.basic.paddingX')};"
            f"border-radius:var(--radius-xl);background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle);"
            f"box-shadow:var(--elevation-1);display:flex;flex-direction:column;"
            f"gap:{sz('card.basic.gap')}}}"
            f".t{{{t('heading3', tokens)}color:var(--color-text-primary)}}"
            f".d{{{t('body2', tokens)}color:var(--color-text-secondary)}}",
        html='<div class="c"><div class="t">카드 제목</div>'
             '<div class="d">보조 설명이 두 줄까지 들어갑니다. 그 이상은 잘라냅니다.</div></div>',
    )
    add(
        id="card-product-md", name="Product Card / MD", group="card",
        tags=["카드", "썸네일", "그리드아이템"],
        spec={"width": "card.width", "radius": "xl", "paddingX": "card.product.paddingX",
              "paddingY": "card.product.paddingY", "gap": "card.product.gap",
              "thumbRatio": "16:9", "borderWidth": "border.width", "elevation": 1},
        tokens={"bg": "surface.default", "border": "border.subtle", "thumb": "surface.sunken"},
        states=["default", "hover", "selected"],
        usage="그리드형 목록의 기본 단위. 3~4열 그리드",
        dont="썸네일 비율을 카드마다 다르게 두지 않음",
        css=f".c{{width:{sz('card.width')};"
            f"padding:{sz('card.product.paddingY')} {sz('card.product.paddingX')};"
            f"border-radius:var(--radius-xl);background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle);"
            f"box-shadow:var(--elevation-1);display:flex;flex-direction:column;"
            f"gap:{sz('card.product.gap')}}}"
            f".th{{aspect-ratio:16/9;border-radius:var(--radius-md);"
            f"background:var(--color-surface-sunken)}}"
            f".t{{{t('body1-bold', tokens)}color:var(--color-text-primary)}}"
            f".d{{{t('caption', tokens)}color:var(--color-text-tertiary)}}",
        html='<div class="c"><div class="th"></div><div><div class="t">프로젝트 이름</div>'
             '<div class="d">2026.08 · 웹사이트 구축</div></div></div>',
    )

    # 숫자 하나를 앞세우는 타일. 테두리·그림자 대신 면을 채워 구분합니다.
    # card-basic 과 다른 물건입니다 — 그쪽은 본문 컨테이너이고 이건 지표 나열용입니다.
    add(
        id="card-stat-md", name="Stat Card / MD", group="card",
        tags=["지표", "숫자", "혜택", "채움형"], since="v1.5.0",
        spec={"width": "card.stat.width", "radius": "xl",
              "paddingX": "card.stat.paddingX", "paddingY": "card.stat.paddingY",
              "gap": "card.stat.gap", "typography": "heading2"},
        tokens={"bg": "surface.sunken", "value": "text.primary",
                "label": "text.primary", "desc": "text.secondary"},
        states=["default"],
        usage="숫자 하나를 앞세우는 지표 묶음. 혜택·실적을 3~4개 나란히 놓을 때",
        dont="숫자가 없으면 쓰지 않음. 그냥 구획이면 card-basic-md",
        css=f".c{{width:{sz('card.stat.width')};"
            f"padding:{sz('card.stat.paddingY')} {sz('card.stat.paddingX')};"
            f"border-radius:var(--radius-xl);background:var(--color-surface-sunken);"
            f"display:flex;flex-direction:column;gap:{sz('card.stat.gap')};"
            f"align-items:center;text-align:center}}"
            f".v{{{t('heading2', tokens)}color:var(--color-text-primary)}}"
            f".l{{{t('body2-bold', tokens)}color:var(--color-text-primary)}}"
            f".d{{{t('caption', tokens)}color:var(--color-text-secondary)}}",
        html='<div class="c"><div class="v">최대 10%</div>'
             '<div class="l">숙박 포인트 적립</div>'
             '<div class="d">공식 홈페이지 예약 기준</div></div>',
    )

    # 세로 썸네일 카드. card-product 와 다른 물건입니다 — 그쪽은 16:9 가로형이고
    # 이건 9:16 세로형이라 그리드 열 수와 스크롤 방식이 달라집니다.
    add(
        id="card-portrait-md", name="Portrait Card / MD", group="card",
        tags=["카드", "세로썸네일", "9:16", "SNS"], since="v1.6.0",
        spec={"width": "card.portrait.width", "radius": "xl",
              "gap": "card.portrait.gap", "thumbRatio": "9:16",
              "typography": "body2"},
        tokens={"bg": "surface.default", "thumb": "surface.sunken",
                "title": "text.primary", "meta": "text.tertiary"},
        states=["default", "hover"],
        usage="세로 이미지가 주인공인 목록. SNS·영상·인물 카드. 4~6열로 늘어놓을 때",
        dont="가로 이미지를 억지로 넣지 않음. 16:9 면 card-product-md",
        css=f".c{{width:{sz('card.portrait.width')};display:flex;flex-direction:column;"
            f"gap:{sz('card.portrait.gap')};background:var(--color-surface-default)}}"
            f".th{{aspect-ratio:9/16;border-radius:var(--radius-xl);"
            f"background:var(--color-surface-sunken)}}"
            f".t{{{t('body2-bold', tokens)}color:var(--color-text-primary)}}"
            f".m{{{t('caption', tokens)}color:var(--color-text-tertiary)}}",
        html='<div class="c"><div class="th"></div>'
             '<div><div class="t">여행지에서 보낸 하루</div>'
             '<div class="m">2026.09 · 브랜드 필름</div></div></div>',
    )

    # ── navigation ──────────────────────────────────────────────────────
    add(
        id="tab-underline-md", name="Tab / Underline / MD", group="navigation",
        tags=["탭", "전환", "같은층위"],
        spec={"width": "tab.width", "height": "tab.height", "gap": "tab.gap",
              "itemPaddingX": "tab.itemPaddingX",
              "indicatorHeight": "tab.indicatorHeight", "typography": "body2-bold"},
        tokens={"indicator": "brand.primary", "labelActive": "text.primary",
                "labelInactive": "text.tertiary", "line": "border.subtle"},
        states=["active", "inactive"],
        usage="같은 층위의 목록을 전환. 2~5개",
        dont="6개 이상이면 탭 대신 드롭다운 필터",
        css=f".c{{display:flex;gap:{sz('tab.gap')};width:{sz('tab.width')};"
            f"height:{sz('tab.height')};align-items:flex-end;"
            f"border-bottom:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".i{{padding:0 {sz('tab.itemPaddingX')} 12px;"
            f"color:var(--color-text-tertiary);{t('body2-bold', tokens)}}}"
            f".i.on{{color:var(--color-text-primary);"
            f"box-shadow:inset 0 calc(-1 * {sz('tab.indicatorHeight')}) 0 "
            f"var(--color-brand-primary)}}",
        html='<div class="c"><div class="i on">전체</div><div class="i">진행중</div>'
             '<div class="i">완료</div></div>',
    )
    add(
        id="pagination-md", name="Pagination / MD", group="navigation",
        tags=["페이지네이션", "목록"],
        spec={"height": "pagination.itemSize", "gap": "pagination.gap",
              "itemSize": "pagination.itemSize", "radius": "md", "typography": "label"},
        tokens={"active": "brand.primary", "label": "text.secondary"},
        states=["default", "current", "disabled"],
        usage="20개 이상 목록. 무한 스크롤이 부적절한 관리 화면",
        dont="10페이지 이상 번호를 다 노출하지 않음. 축약 표기 사용",
        css=f".c{{display:flex;gap:{sz('pagination.gap')};align-items:center}}"
            f".p{{width:{sz('pagination.itemSize')};height:{sz('pagination.itemSize')};"
            f"display:flex;align-items:center;justify-content:center;"
            f"border-radius:var(--radius-md);color:var(--color-text-secondary);{t('label', tokens)}}}"
            f".p.on{{background:var(--color-brand-primary);color:var(--color-text-inverse)}}",
        html='<div class="c"><div class="p">‹</div><div class="p on">1</div>'
             '<div class="p">2</div><div class="p">3</div><div class="p">›</div></div>',
    )

    # ── table ───────────────────────────────────────────────────────────
    add(
        id="table-basic-lg", name="Table / Basic / LG", group="table",
        tags=["테이블", "목록", "관리화면"],
        spec={"width": "table.width", "rowHeight": "table.rowHeight",
              "headerHeight": "table.headerHeight", "paddingX": "table.paddingX",
              "borderWidth": "border.width", "radius": "xl", "typography": "body2"},
        tokens={"header": "surface.subtle", "border": "border.subtle", "label": "text.secondary"},
        states=["default", "hover", "selected"],
        usage="비교가 필요한 목록. 열이 3개 이상일 때",
        dont="모바일에서 그대로 쓰지 않음. 카드로 전환",
        css=f".c{{width:{sz('table.width')};"
            f"border:{sz('border.width')} solid var(--color-border-subtle);"
            f"border-radius:var(--radius-lg);overflow:hidden}}"
            f"table{{width:100%;border-collapse:collapse}}"
            f"th{{height:{sz('table.headerHeight')};padding:0 {sz('table.paddingX')};"
            f"text-align:left;background:var(--color-surface-subtle);"
            f"color:var(--color-text-secondary);{t('caption-bold', tokens)}}}"
            f"td{{height:{sz('table.rowHeight')};padding:0 {sz('table.paddingX')};"
            f"border-top:{sz('border.width')} solid var(--color-border-subtle);"
            f"color:var(--color-text-primary);{t('body2', tokens)}}}"
            f"td.n{{font-variant-numeric:tabular-nums;text-align:right}}",
        html='<div class="c"><table><thead><tr><th>프로젝트</th><th>담당</th>'
             '<th style="text-align:right">진행률</th></tr></thead><tbody>'
             '<tr><td>프로젝트 A</td><td>디자인팀</td><td class="n">72%</td></tr>'
             '<tr><td>프로젝트 B</td><td>개발팀</td><td class="n">40%</td></tr>'
             '</tbody></table></div>',
    )

    # ── feedback ────────────────────────────────────────────────────────
    toast = (f"display:flex;align-items:center;gap:{sz('toast.gap')};"
             f"width:{sz('toast.width')};"
             f"padding:{sz('toast.paddingY')} {sz('toast.paddingX')};"
             f"border-radius:var(--radius-lg);box-shadow:var(--elevation-2);")
    add(
        id="toast-info-md", name="Toast / Info / MD", group="feedback",
        tags=["토스트", "알림", "완료"],
        spec={"width": "toast.width", "radius": "xl", "paddingX": "toast.paddingX",
              "paddingY": "toast.paddingY", "gap": "toast.gap",
              "elevation": 2, "typography": "body2", "duration": 4000},
        tokens={"bg": "surface.inverse", "label": "text.inverse"},
        usage="되돌릴 필요 없는 결과 통보. 4초 후 자동 사라짐",
        dont="에러나 확인이 필요한 내용에 쓰지 않음. 사용자가 놓침",
        css=f".c{{{toast}background:var(--color-surface-inverse);color:var(--color-text-inverse);"
            f"{t('body2', tokens)}}}",
        html='<div class="c"><span>✓</span><span>저장했습니다</span></div>',
    )
    add(
        id="toast-error-md", name="Toast / Error / MD", group="feedback",
        tags=["토스트", "에러"],
        spec={"width": "toast.width", "radius": "xl", "paddingX": "toast.paddingX",
              "paddingY": "toast.paddingY", "gap": "toast.gap",
              "borderWidth": "border.width", "elevation": 2, "typography": "body2"},
        tokens={"bg": "danger.subtle", "border": "border.danger", "label": "danger.text"},
        usage="실패 통보. 자동으로 사라지지 않고 사용자가 닫음",
        dont="원인 설명 없이 '오류가 발생했습니다'만 쓰지 않음",
        css=f".c{{{toast}background:var(--color-danger-subtle);"
            f"border:{sz('border.width')} solid var(--color-border-danger);"
            f"color:var(--color-danger-text);"
            f"{t('body2', tokens)}}}",
        html='<div class="c"><span>!</span><span>네트워크 연결을 확인해 주세요</span></div>',
    )
    add(
        id="badge-status-sm", name="Status Badge / SM", group="badge",
        tags=["뱃지", "상태", "라벨"],
        spec={"height": "badge.height", "radius": "full", "paddingX": "badge.paddingX",
              "typography": "caption-bold"},
        tokens={"bg": "success.subtle", "label": "success.default"},
        states=["success", "warning", "danger", "neutral"],
        usage="행·카드의 상태 표기. 색과 텍스트를 함께 씀",
        dont="색만으로 상태를 구분하지 않음",
        css=f".c{{display:inline-flex;gap:8px}}"
            f".b{{display:inline-flex;align-items:center;height:{sz('badge.height')};"
            f"padding:0 {sz('badge.paddingX')};"
            f"border-radius:var(--radius-full);{t('caption-bold', tokens)}}}"
            f".s{{background:var(--color-success-subtle);color:var(--color-success-default)}}"
            f".w{{background:var(--color-warning-subtle);color:var(--color-warning-default)}}"
            f".d{{background:var(--color-danger-subtle);color:var(--color-danger-text)}}",
        html='<div class="c"><span class="b s">완료</span><span class="b w">검토중</span>'
             '<span class="b d">지연</span></div>',
    )
    add(
        id="modal-confirm-lg", name="Confirm Modal / LG", group="modal",
        tags=["모달", "확인", "파괴적액션"],
        spec={"width": "modal.width", "radius": "xl", "paddingX": "modal.paddingX",
              "paddingY": "modal.paddingY", "gap": "modal.gap",
              "elevation": 3, "typography": "heading3"},
        tokens={"bg": "surface.default", "title": "text.primary", "body": "text.secondary"},
        usage="되돌릴 수 없는 액션 직전의 확인",
        dont="단순 안내에 쓰지 않음. 그건 토스트",
        css=f".c{{width:{sz('modal.width')};"
            f"padding:{sz('modal.paddingY')} {sz('modal.paddingX')};"
            f"border-radius:var(--radius-xl);"
            f"background:var(--color-surface-default);box-shadow:var(--elevation-3);"
            f"display:flex;flex-direction:column;gap:{sz('modal.gap')}}}"
            f".t{{{t('heading3', tokens)}color:var(--color-text-primary)}}"
            f".d{{{t('body2', tokens)}color:var(--color-text-secondary);margin-top:8px}}"
            f".r{{display:flex;gap:8px;justify-content:flex-end}}"
            f".bs,.bd{{height:44px;padding:0 18px;border:0;border-radius:var(--radius-md);"
            f"{t('body2-bold', tokens)}}}"
            f".bs{{background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-primary)}}"
            f".bd{{background:var(--color-danger-default);color:var(--color-text-inverse)}}",
        html='<div class="c"><div><div class="t">프로젝트를 삭제할까요?</div>'
             '<div class="d">삭제하면 시안 12건과 이력이 함께 사라집니다. 되돌릴 수 없습니다.</div>'
             '</div><div class="r"><button class="bs">취소</button>'
             '<button class="bd">삭제</button></div></div>',
    )

    # ── button / outline ────────────────────────────────────────────────
    # 테두리를 border.brand 로 잡습니다. secondary(중립 회색 테두리)보다 위계가 높고,
    # 채움형 primary 가 반복되면 시끄러워지는 목록 화면을 위한 자리입니다.
    for size, rad, typ in [("lg", "lg", "body1-bold"),
                           ("md", "md", "body2-bold")]:
        add(
            id=f"btn-outline-{size}", name=f"Outline Button / {size.upper()}", group="button",
            tags=["CTA", "테두리형", "반복액션"], since="v1.0.3",
            spec={"width": "hug", "height": f"control.{size}.height", "radius": rad,
                  "paddingX": f"control.{size}.paddingX",
                  "borderWidth": "border.width", "typography": typ},
            tokens={"bg": "surface.default", "border": "border.brand", "label": "text.brand"},
            states=["default", "hover", "pressed", "disabled"],
            usage={"lg": "채움형이 과한 화면의 주요 액션. 버튼이 화면에서 여러 번 반복될 때",
                   "md": "카드·행 안의 반복 액션. 장바구니 담기·상세 보기"}[size],
            dont="btn-primary와 같은 화면에 섞지 않음. 어느 쪽이 주요 액션인지 흐려짐",
            css=f".c{{{btn_base}height:{sz(f'control.{size}.height')};"
                f"padding:0 {sz(f'control.{size}.paddingX')};"
                f"border-radius:var(--radius-{rad});"
                f"background:var(--color-surface-default);"
                f"border:{sz('border.width')} solid var(--color-border-brand);"
                f"color:var(--color-text-brand);"
                f"{t(typ, tokens)}}}",
            html='<button class="c">장바구니 담기</button>',
        )

    # ── commerce ────────────────────────────────────────────────────────
    add(
        id="price-discount-md", name="Price / Discount / MD", group="commerce",
        tags=["가격", "할인", "커머스"], since="v1.0.3",
        spec={"gap": "price.gap", "typography": "body1-bold",
              "originalTypography": "caption"},
        tokens={"rate": "text.brand", "price": "text.primary", "original": "text.tertiary"},
        usage="할인율·판매가·정가를 한 줄로. 목록과 상세에서 순서를 바꾸지 않음",
        dont="정가에 취소선 없이 두 가격을 나란히 두지 않음. 어느 쪽이 낼 돈인지 알 수 없음",
        css=f".c{{display:inline-flex;align-items:baseline;gap:{sz('price.gap')};"
            f"white-space:nowrap}}"
            f".r{{{t('body1-bold', tokens)}color:var(--color-text-brand)}}"
            f".p{{{t('body1-bold', tokens)}color:var(--color-text-primary)}}"
            f".o{{{t('caption', tokens)}color:var(--color-text-tertiary);"
            f"text-decoration:line-through}}",
        html='<div class="c"><span class="r">10%</span>'
             '<span class="p">1,023,000원</span>'
             '<span class="o">1,137,000원</span></div>',
    )

    wish = (f"display:inline-flex;align-items:center;justify-content:center;"
            f"width:{sz('toggle.size')};height:{sz('toggle.size')};"
            f"border-radius:var(--radius-full);cursor:pointer;"
            f"font-family:inherit;font-size:{sz('toggle.iconSize')};line-height:1;")
    add(
        id="wish-toggle-md", name="Wish Toggle / MD", group="commerce",
        tags=["찜", "관심", "토글"], since="v1.0.3",
        spec={"width": "toggle.size", "height": "toggle.size", "radius": "full",
              "borderWidth": "border.width", "iconSize": "toggle.iconSize"},
        tokens={"bg": "surface.default", "border": "border.subtle", "icon": "text.tertiary"},
        states=["default", "selected"],
        usage="목록 카드의 관심 등록. 40x40 터치 영역을 확보한 최소 크기",
        dont="선택 상태를 색으로만 표시하지 않음. 하트를 채워 모양도 함께 바꿈",
        css=f".c{{{wish}background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle);"
            f"color:var(--color-text-tertiary)}}",
        html='<button class="c" aria-label="관심 등록">\u2661</button>',
    )
    add(
        id="wish-toggle-md-selected", variantOf="wish-toggle-md", variantState="selected", name="Wish Toggle / MD / Selected", group="commerce",
        tags=["찜", "관심", "토글", "선택됨"], since="v1.0.3",
        spec={"width": "toggle.size", "height": "toggle.size", "radius": "full",
              "borderWidth": "border.width", "iconSize": "toggle.iconSize"},
        tokens={"bg": "brand.subtle", "border": "brand.primary", "icon": "brand.onSubtle"},
        states=["selected"],
        usage="관심 등록된 상태. 배경 채움 + 테두리 + 채운 하트로 삼중 표기",
        dont="기본 상태와 하트 모양이 같으면 안 됨. 색각 이상 사용자가 구분하지 못함",
        css=f".c{{{wish}background:var(--color-brand-subtle);"
            f"border:{sz('border.width')} solid var(--color-brand-primary);"
            f"color:var(--color-brand-onSubtle)}}",
        html='<button class="c" aria-label="관심 해제" aria-pressed="true">\u2665</button>',
    )

    # ── layout ──────────────────────────────────────────────────────────
    # 랜딩 다섯 건에서 매번 손으로 만들던 묶음입니다. 아이브로우는 선택 요소로,
    # 없으면 .e 를 빼면 됩니다.
    add(
        id="section-header-md", name="Section Header / MD", group="layout",
        tags=["섹션", "제목", "리드문"], since="v1.0.4",
        spec={"gap": "section.gap", "eyebrowTypography": "label", "eyebrowTracking": "0.1em",
              "titleTypography": "heading1", "leadTypography": "body1",
              "leadMaxWidth": "58ch"},
        tokens={"eyebrow": "text.brand", "title": "text.primary", "lead": "text.secondary"},
        states=["default", "아이브로우 없음"],
        usage="섹션 시작의 제목 묶음. 아이브로우(선택) · 제목 · 리드문을 한 덩어리로",
        dont="리드문이 세 줄을 넘기면 리드가 아니라 본문. 본문은 섹션 안으로 내림",
        css=f".c{{display:flex;flex-direction:column;gap:{sz('section.gap')}}}"
            f".e{{{t('label', tokens)}letter-spacing:0.1em;text-transform:uppercase;"
            f"color:var(--color-text-brand)}}"
            f".t{{{t('heading1', tokens)}color:var(--color-text-primary)}}"
            f".l{{{t('body1', tokens)}color:var(--color-text-secondary);max-width:58ch}}",
        html='<div class="c"><div class="e">오늘 자른 꽃</div>'
             '<div class="t">이번 주 인기 상품</div>'
             '<div class="l">계절에 나온 꽃으로 그때그때 다르게 묶습니다.</div></div>',
    )

    # 여기부터가 "페이지를 이루는 덩어리" 입니다. v1.7.1 까지 이 자리가 비어 있어서
    # 헤더·히어로·푸터·폼 묶음을 화면마다 손으로 그렸고, 그릴 때마다 모양이 달라졌습니다.
    # 원자(버튼·입력·칩)는 충분한데 원자를 놓을 판이 없었던 것입니다.
    add(
        id="header-gnb-lg", name="Header / GNB / LG", group="layout",
        tags=["헤더", "GNB", "전역내비"], since="v1.8.0",
        spec={"width": "container.max", "height": "header.height",
              "itemGap": "header.itemGap", "borderWidth": "border.width",
              "logoTypography": "heading3", "menuTypography": "body2-bold",
              "actionHeight": "control.md.height"},
        tokens={"bg": "surface.default", "border": "border.subtle",
                "logo": "text.brand", "menu": "text.secondary",
                "menuActive": "text.primary"},
        states=["default", "현재 메뉴", "스크롤 고정", "메뉴 접힘"],
        usage="모든 페이지 최상단. 로고 · 주 메뉴 · 주요 액션 하나",
        dont="메뉴가 7개를 넘기면 여기 다 넣지 않음. 드롭다운이나 2단으로 나눔",
        css=f".c{{width:{lay('container.max')};height:{sz('header.height')};"
            f"display:flex;align-items:center;gap:{sz('header.itemGap')};"
            f"padding:0 {lay('container.gutter')};"
            f"background:var(--color-surface-default);"
            f"border-bottom:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".lg{{{t('heading3', tokens)}color:var(--color-text-brand);white-space:nowrap}}"
            f".nv{{display:flex;gap:{sz('header.itemGap')};margin-left:auto}}"
            f".nv span{{{t('body2-bold', tokens)}color:var(--color-text-secondary);"
            f"white-space:nowrap}}"
            f".nv span.on{{color:var(--color-text-primary)}}"
            f".ac{{{btn_base}height:{sz('control.md.height')};"
            f"padding:0 {sz('control.md.paddingX')};border-radius:var(--radius-md);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"{t('body2-bold', tokens)}}}",
        html='<div class="c"><div class="lg">ELUON</div>'
             '<div class="nv"><span class="on">사업</span><span>계열</span>'
             '<span>연혁</span><span>뉴스</span></div>'
             '<button class="ac">문의하기</button></div>',
    )

    add(
        id="hero-split-lg", name="Hero / Split / LG", group="layout",
        tags=["히어로", "첫화면", "2단"], since="v1.8.0",
        spec={"width": "container.max", "gap": "hero.gap",
              "actionGap": "hero.actionGap", "railGap": "hero.railGap",
              "borderWidth": "border.width", "titleTypography": "display1",
              "leadTypography": "body1", "leadMaxWidth": "60ch"},
        tokens={"eyebrow": "text.brand", "title": "text.primary",
                "lead": "text.secondary", "rail": "border.default",
                "railLabel": "text.tertiary", "railValue": "text.primary"},
        states=["default", "레일 없음"],
        usage="페이지 첫 화면. 제목·리드·액션을 왼쪽에, 핵심 수치 레일을 오른쪽에",
        dont="한 화면에 두 번 쓰지 않음. 무엇이 이 페이지의 주제인지 흐려짐",
        css=f".c{{width:{lay('container.max')};display:grid;"
            f"grid-template-columns:minmax(0,7fr) minmax(0,5fr);"
            f"gap:{sz('hero.gap')};align-items:end;"
            f"padding:0 {lay('container.gutter')}}}"
            f".e{{{t('label', tokens)}letter-spacing:0.1em;text-transform:uppercase;"
            f"color:var(--color-text-brand)}}"
            f".t{{{t('display1', tokens)}color:var(--color-text-primary);margin-top:12px}}"
            f".l{{{t('body1', tokens)}color:var(--color-text-secondary);"
            f"max-width:60ch;margin-top:{sz('hero.railGap')}}}"
            f".a{{display:flex;gap:{sz('hero.actionGap')};margin-top:32px}}"
            f".b1,.b2{{{btn_base}height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"{t('body1-bold', tokens)}}}"
            f".b1{{background:var(--color-brand-primary);color:var(--color-text-inverse)}}"
            f".b2{{background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"color:var(--color-text-primary)}}"
            f".r{{border-left:{sz('border.width')} solid var(--color-border-default);"
            f"padding-left:24px;display:flex;flex-direction:column;"
            f"gap:{sz('hero.railGap')}}}"
            f".rl{{{t('caption', tokens)}color:var(--color-text-tertiary);"
            f"letter-spacing:0.06em;text-transform:uppercase}}"
            f".rv{{{t('heading3', tokens)}color:var(--color-text-primary);"
            f"font-variant-numeric:tabular-nums}}",
        html='<div class="c"><div><div class="e">Holding Company</div>'
             '<div class="t">이동을 잇고,<br>머무름을 설계합니다</div>'
             '<div class="l">항공·물류·호텔 세 축으로 사람과 물자의 이동 전 과정을 연결합니다.</div>'
             '<div class="a"><button class="b1">사업 구조 보기</button>'
             '<button class="b2">연차보고서</button></div></div>'
             '<div class="r"><div><div class="rl">설립</div><div class="rv">1962년</div></div>'
             '<div><div class="rl">계열사</div><div class="rv">11개사</div></div>'
             '<div><div class="rl">임직원</div><div class="rv">27,400명</div></div></div></div>',
    )

    add(
        id="cta-band-lg", name="CTA Band / LG", group="layout",
        tags=["CTA", "전환", "띠"], since="v1.8.0",
        spec={"width": "container.max", "paddingY": "ctaBand.paddingY",
              "gap": "ctaBand.gap", "radius": "xl",
              "titleTypography": "heading1", "leadTypography": "body1"},
        tokens={"bg": "brand.primary", "title": "text.inverse", "lead": "text.inverse",
                "actionBg": "surface.default", "actionLabel": "text.brand"},
        states=["default"],
        usage="섹션과 섹션 사이, 또는 페이지 끝의 전환 유도. 한 페이지에 하나",
        dont="본문 정보를 여기 넣지 않음. 제목 한 줄·리드 한 줄·버튼 하나까지",
        css=f".c{{width:{lay('container.max')};"
            f"padding:{sz('ctaBand.paddingY')} {lay('container.gutter')};"
            f"border-radius:var(--radius-xl);background:var(--color-brand-primary);"
            f"display:flex;align-items:center;justify-content:space-between;"
            f"gap:{sz('ctaBand.gap')}}}"
            f".t{{{t('heading1', tokens)}color:var(--color-text-inverse)}}"
            f".l{{{t('body1', tokens)}color:var(--color-text-inverse);margin-top:8px}}"
            f".b{{{btn_base}height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"background:var(--color-surface-default);color:var(--color-text-brand);"
            f"{t('body1-bold', tokens)};flex:none}}",
        html='<div class="c"><div><div class="t">제안이 필요하신가요</div>'
             '<div class="l">영업일 기준 2일 안에 담당자가 회신합니다.</div></div>'
             '<button class="b">문의 보내기</button></div>',
    )

    add(
        id="footer-lg", name="Footer / LG", group="layout",
        tags=["푸터", "전역", "고지"], since="v1.8.0",
        spec={"width": "container.max", "paddingY": "footer.paddingY",
              "gap": "footer.gap", "logoTypography": "heading3",
              "noteTypography": "caption", "menuTypography": "caption"},
        tokens={"bg": "surface.inverse", "logo": "text.inverse",
                "note": "text.inverse", "menu": "text.inverse"},
        states=["default"],
        usage="모든 페이지 최하단. 로고 · 고지 · 보조 메뉴",
        dont="색을 흐리게 해서 구분하지 않음. 뒤집힌 면에서는 대비가 무너짐. 크기와 굵기로 나눔",
        css=f".c{{width:{lay('container.max')};"
            f"padding:{sz('footer.paddingY')} {lay('container.gutter')};"
            f"background:var(--color-surface-inverse);display:flex;"
            f"justify-content:space-between;align-items:baseline;"
            f"gap:{sz('footer.gap')}}}"
            f".lg{{{t('heading3', tokens)}color:var(--color-text-inverse)}}"
            f".n{{{t('caption', tokens)}color:var(--color-text-inverse);"
            f"max-width:56ch;margin-top:12px;opacity:.72}}"
            f".m{{display:flex;gap:20px}}"
            f".m span{{{t('caption', tokens)}color:var(--color-text-inverse);opacity:.72;"
            f"white-space:nowrap}}",
        html='<div class="c"><div><div class="lg">ELUON</div>'
             '<div class="n">서울특별시 · 대표전화 02-0000-0000 · '
             '이 페이지의 내용은 예시입니다.</div></div>'
             '<div class="m"><span>회사소개</span><span>개인정보처리방침</span>'
             '<span>이용약관</span></div></div>',
    )

    add(
        id="form-field-md", name="Form Field / MD", group="layout",
        tags=["폼", "라벨", "도움말"], since="v1.8.0",
        spec={"width": "field.width", "labelGap": "field.labelGap",
              "helperGap": "field.helperGap", "inputHeight": "field.height",
              "radius": "md", "paddingX": "field.paddingX",
              "borderWidth": "border.width", "labelTypography": "label",
              "helperTypography": "caption"},
        tokens={"label": "text.primary", "border": "border.default",
                "placeholder": "text.tertiary", "helper": "text.secondary"},
        states=["default", "focus", "error", "disabled", "도움말 없음"],
        usage="라벨 · 입력 · 도움말을 한 묶음으로. 폼의 최소 단위",
        dont="라벨을 placeholder 로 대신하지 않음. 입력하면 라벨이 사라짐",
        css=f".c{{width:{sz('field.width')};display:flex;flex-direction:column;"
            f"gap:{sz('field.labelGap')}}}"
            f".lb{{{t('label', tokens)}color:var(--color-text-primary)}}"
            f".in{{height:{sz('field.height')};padding:0 {sz('field.paddingX')};"
            f"display:flex;align-items:center;border-radius:var(--radius-md);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"background:var(--color-surface-default);"
            f"color:var(--color-text-tertiary);{t('body2', tokens)}}}"
            f".hp{{{t('caption', tokens)}color:var(--color-text-secondary);"
            f"margin-top:calc({sz('field.helperGap')} - {sz('field.labelGap')})}}",
        html='<div class="c"><div class="lb">회신 받을 메일</div>'
             '<div class="in">name@example.com</div>'
             '<div class="hp">영업일 기준 2일 안에 회신합니다.</div></div>',
    )

    add(
        id="list-row-md", name="List Row / MD", group="layout",
        tags=["목록", "행", "뉴스"], since="v1.8.0",
        spec={"paddingY": "listRow.paddingY", "gap": "listRow.gap",
              "borderWidth": "border.width", "titleTypography": "body1-bold",
              "metaTypography": "caption", "valueTypography": "body2-bold"},
        tokens={"border": "border.subtle", "title": "text.primary",
                "meta": "text.tertiary", "value": "text.primary"},
        states=["default", "hover", "값 없음"],
        usage="제목·메타·값이 한 줄인 목록. 공지·뉴스·자료실",
        dont="열이 셋을 넘게 비교해야 하면 목록이 아니라 표. table-basic-lg 로",
        css=f".c{{display:flex;flex-direction:column}}"
            f".rw{{display:flex;align-items:baseline;gap:{sz('listRow.gap')};"
            f"padding:{sz('listRow.paddingY')} 0;"
            f"border-bottom:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".tx{{flex:1;min-width:0}}"
            f".t{{{t('body1-bold', tokens)}color:var(--color-text-primary)}}"
            f".m{{{t('caption', tokens)}color:var(--color-text-tertiary);margin-top:4px}}"
            f".v{{{t('body2-bold', tokens)}color:var(--color-text-primary);"
            f"font-variant-numeric:tabular-nums;white-space:nowrap}}",
        html='<div class="c">'
             '<div class="rw"><div class="tx"><div class="t">2024년 3분기 실적 공시</div>'
             '<div class="m">공시</div></div><div class="v">2024.11.28</div></div>'
             '<div class="rw"><div class="tx"><div class="t">신규 노선 취항 안내</div>'
             '<div class="m">보도자료</div></div><div class="v">2024.11.14</div></div>'
             '</div>',
    )

    # ── 보조 어휘 ────────────────────────────────────────────────────────
    # 여기부터는 한글 본문이 실제로 들어가는 자리입니다. keep-all 만으로는
    # 긴 영문·URL 이 넘치고, 넘치면 레이아웃이 통째로 밀립니다.
    add(
        id="accordion-md", name="Accordion / MD", group="disclosure",
        tags=["아코디언", "FAQ", "약관", "접기"], since="v1.10.0",
        spec={"paddingY": "accordion.paddingY", "gap": "accordion.gap",
              "borderWidth": "border.width", "iconSize": "accordion.iconSize",
              "titleTypography": "body1-bold", "bodyTypography": "body2",
              "bodyMaxWidth": "text.measure"},
        tokens={"border": "border.subtle", "title": "text.primary",
                "body": "text.secondary", "icon": "text.tertiary",
                "titleOpen": "text.brand"},
        states=["closed", "open", "hover"],
        usage="질문·항목이 길어 한 번에 다 보이면 부담스러운 목록. FAQ·약관·상세 사양",
        dont="한 번에 다 읽어야 하는 내용을 접지 않음. 접힌 것은 안 읽습니다",
        css=f".c{{display:flex;flex-direction:column}}"
            f".it{{border-bottom:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".hd{{display:flex;align-items:flex-start;gap:{sz('accordion.gap')};"
            f"padding:{sz('accordion.paddingY')} 0;cursor:pointer}}"
            f".q{{flex:1;min-width:0;{t('body1-bold', tokens)}"
            f"color:var(--color-text-primary);{KO}}}"
            f".it.on .q{{color:var(--color-text-brand)}}"
            f".ic{{flex:none;width:{sz('accordion.iconSize')};"
            f"height:{sz('accordion.iconSize')};line-height:{sz('accordion.iconSize')};"
            f"text-align:center;color:var(--color-text-tertiary)}}"
            f".bd{{padding:0 0 {sz('accordion.paddingY')};max-width:{lay('text.measure')};"
            f"{t('body2', tokens)}color:var(--color-text-secondary);{KO}}}",
        html='<div class="c">'
             '<div class="it on"><div class="hd"><div class="q">'
             '제안서에 들어가는 자산은 어디까지 정해져 있나요?</div>'
             '<div class="ic">\u2212</div></div>'
             '<div class="bd">규격·색·라운드·간격까지 manifest 에 적혀 있습니다. '
             '화면을 만드는 사람이 정하는 것은 무엇을 어디에 놓느냐뿐입니다.</div></div>'
             '<div class="it"><div class="hd"><div class="q">'
             '고객사마다 크기가 다른데 컴포넌트를 새로 만들어야 하나요?</div>'
             '<div class="ic">+</div></div></div>'
             '</div>',
    )

    add(
        id="breadcrumb-md", name="Breadcrumb / MD", group="navigation",
        tags=["경로", "브레드크럼", "깊은구조"], since="v1.10.0",
        spec={"gap": "breadcrumb.gap", "itemMaxWidth": "breadcrumb.itemMaxWidth",
              "typography": "caption"},
        tokens={"link": "text.tertiary", "current": "text.primary",
                "separator": "text.tertiary"},
        states=["default", "현재 위치", "말줄임"],
        usage="세 단계 이상 깊은 페이지의 현재 위치. 목록 → 분류 → 상세",
        dont="두 단계뿐인 구조에 쓰지 않음. 뒤로 가기 한 번이면 됩니다",
        css=f".c{{display:flex;align-items:center;gap:{sz('breadcrumb.gap')};"
            f"flex-wrap:wrap;{t('caption', tokens)}}}"
            # 한글 항목명이 길면 줄을 통째로 밀어냅니다. 항목마다 상한을 두고 말줄임합니다.
            f".i{{max-width:{sz('breadcrumb.itemMaxWidth')};overflow:hidden;"
            f"text-overflow:ellipsis;white-space:nowrap;color:var(--color-text-tertiary)}}"
            f".i.on{{color:var(--color-text-primary);font-weight:700}}"
            f".s{{color:var(--color-text-tertiary);flex:none}}",
        html='<div class="c"><span class="i">홈</span><span class="s">/</span>'
             '<span class="i">사업 소개</span><span class="s">/</span>'
             '<span class="i">물류·터미널 부문 운영 현황</span><span class="s">/</span>'
             '<span class="i on">내륙 거점 안내</span></div>',
    )

    add(
        id="empty-state-md", name="Empty State / MD", group="feedback",
        tags=["빈상태", "결과없음", "안내"], since="v1.10.0",
        spec={"paddingY": "empty.paddingY", "gap": "empty.gap",
              "titleTypography": "body1-bold", "bodyTypography": "body2",
              "bodyMaxWidth": "empty.bodyMaxWidth"},
        tokens={"bg": "surface.subtle", "title": "text.primary",
                "body": "text.secondary"},
        states=["결과 없음", "아직 없음", "권한 없음"],
        usage="목록이 비었을 때. 왜 비었는지와 다음에 무엇을 할지를 같이 적음",
        dont="'데이터가 없습니다'만 쓰지 않음. 왜 없는지·무엇을 하면 되는지가 빠지면 막힙니다",
        css=f".c{{display:flex;flex-direction:column;align-items:center;"
            f"text-align:center;gap:{sz('empty.gap')};"
            f"padding:{sz('empty.paddingY')} {sz('empty.gap')};"
            f"background:var(--color-surface-subtle);border-radius:var(--radius-xl)}}"
            f".t{{{t('body1-bold', tokens)}color:var(--color-text-primary);{KO}}}"
            f".d{{{t('body2', tokens)}color:var(--color-text-secondary);"
            f"max-width:{sz('empty.bodyMaxWidth')};{KO}}}"
            f".b{{{btn_base}height:{sz('control.md.height')};"
            f"padding:0 {sz('control.md.paddingX')};border-radius:var(--radius-md);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"{t('body2-bold', tokens)};margin-top:4px}}",
        html='<div class="c"><div class="t">조건에 맞는 자료가 없습니다</div>'
             '<div class="d">기간을 넓히거나 분류를 전체로 바꾸면 더 나올 수 있습니다.</div>'
             '<button class="b">조건 초기화</button></div>',
    )

    add(
        id="desc-list-md", name="Description List / MD", group="layout",
        tags=["정의목록", "개요", "사양"], since="v1.10.0",
        spec={"labelWidth": "descList.labelWidth", "rowPaddingY": "descList.rowPaddingY",
              "gap": "descList.gap", "borderWidth": "border.width",
              "labelTypography": "body2-bold", "valueTypography": "body2"},
        tokens={"border": "border.subtle", "label": "text.secondary",
                "value": "text.primary"},
        states=["default", "값 여러 줄"],
        usage="라벨과 값이 짝인 목록. 회사 개요·사양·계약 조건",
        dont="비교가 필요하면 목록이 아니라 표. table-basic-lg 로",
        css=f".c{{display:flex;flex-direction:column;margin:0}}"
            f".r{{display:flex;gap:{sz('descList.gap')};"
            f"padding:{sz('descList.rowPaddingY')} 0;"
            f"border-bottom:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".k{{flex:0 0 {sz('descList.labelWidth')};margin:0;"
            f"{t('body2-bold', tokens)}color:var(--color-text-secondary);{KO}}}"
            f".v{{flex:1;min-width:0;margin:0;{t('body2', tokens)}"
            f"color:var(--color-text-primary);{NUM}{KO}}}",
        html='<dl class="c">'
             '<div class="r"><dt class="k">설립</dt><dd class="v">1962년 3월 (법인 전환 1978년)</dd></div>'
             '<div class="r"><dt class="k">본사</dt>'
             '<dd class="v">서울특별시 중구 세종대로 000, 코발트빌딩 14~17층</dd></div>'
             '<div class="r"><dt class="k">임직원</dt><dd class="v">27,400명 (2024.12 기준)</dd></div>'
             '</dl>',
    )

    add(
        id="step-flow-md", name="Step Flow / MD", group="layout",
        tags=["절차", "단계", "안내"], since="v1.10.0",
        spec={"gap": "stepFlow.gap", "numberSize": "stepFlow.numberSize",
              "rowGap": "stepFlow.rowGap", "borderWidth": "border.width",
              "titleTypography": "body1-bold", "bodyTypography": "body2",
              "bodyMaxWidth": "text.measure"},
        tokens={"number": "text.inverse", "numberBg": "brand.primary",
                "title": "text.primary", "body": "text.secondary",
                "line": "border.subtle"},
        states=["default", "완료", "현재 단계"],
        usage="순서가 있는 절차. 신청 방법·심사 과정·이용 안내",
        dont="순서가 없는 목록에 번호를 붙이지 않음. 번호는 순서가 있다는 약속입니다",
        css=f".c{{display:flex;flex-direction:column;gap:{sz('stepFlow.rowGap')}}}"
            f".s{{display:flex;gap:{sz('stepFlow.gap')};align-items:flex-start}}"
            f".n{{flex:none;width:{sz('stepFlow.numberSize')};"
            f"height:{sz('stepFlow.numberSize')};border-radius:var(--radius-full);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"display:flex;align-items:center;justify-content:center;"
            f"{t('caption-bold', tokens)}{NUM}}}"
            f".tx{{flex:1;min-width:0;max-width:{lay('text.measure')}}}"
            f".t{{{t('body1-bold', tokens)}color:var(--color-text-primary);{KO}}}"
            f".d{{{t('body2', tokens)}color:var(--color-text-secondary);margin-top:4px;{KO}}}",
        html='<div class="c">'
             '<div class="s"><div class="n">1</div><div class="tx">'
             '<div class="t">신청서 접수</div>'
             '<div class="d">온라인 양식으로만 받습니다. 영업일 기준 2일 안에 접수 확인 메일이 갑니다.</div>'
             '</div></div>'
             '<div class="s"><div class="n">2</div><div class="tx">'
             '<div class="t">서류 검토</div>'
             '<div class="d">담당 부서가 사업자등록증과 최근 3개년 재무제표를 확인합니다.</div>'
             '</div></div>'
             '<div class="s"><div class="n">3</div><div class="tx">'
             '<div class="t">결과 통보</div>'
             '<div class="d">검토 완료 후 신청 시 적으신 메일로 결과를 보내드립니다.</div>'
             '</div></div>'
             '</div>',
    )

    for c in C:
        c["responsive"] = RESPONSIVE.get(c["id"], {})
    return C

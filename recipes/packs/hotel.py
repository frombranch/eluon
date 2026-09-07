# -*- coding: utf-8 -*-
"""hotel pack — 예약 도메인 자산 (주차 중, 아직 파이프라인에 배선되지 않음).

CLAUDE.md 의 core/pack/site 3층 구조가 확정되면 여기서 build() 로 승격합니다.
core 는 "공통으로 쓰이는 것"이 아니라 "업종이 바뀌어도 참인 것"이므로
예약 어휘는 core 에 두지 않습니다.
치수 토큰은 tokens/pack-hotel.json 에 있습니다.
"""

RESPONSIVE = {
    "booking-bar-lg":  {"md": "stack"},
    "stay-summary-md": {"md": "stack"},
    "rate-card-lg":    {"md": "stack"},
    "date-range-md":   {"md": "fill"},
}

def build(tokens, add, t, sz, lay, btn_base, KO, NUM):
    """components.build() 의 헬퍼를 그대로 받아 예약 자산을 추가합니다."""
    # ── 예약(booking) ──────────────────────────────────────────────
    # 숙박·항공·공연처럼 "날짜와 인원을 정해 값을 확정하는" 업무의 부품입니다.
    # 커머스(장바구니·할인율)와 다른 물건입니다 — 그쪽은 commerce 그룹입니다.

    add(
        id="booking-bar-lg", name="Booking Bar / LG", group="booking",
        tags=["예약", "검색", "숙박"], since="v1.13.0",
        spec={"width": "container.max", "paddingY": "booking.barPaddingY",
              "gap": "booking.barGap", "fieldGap": "booking.fieldGap",
              "borderWidth": "border.width",
              "labelTypography": "label", "valueTypography": "body1-bold",
              "actionHeight": "control.lg.height",
              "actionPaddingX": "control.lg.paddingX"},
        tokens={"bg": "surface.default", "border": "border.subtle",
                "label": "text.secondary", "value": "text.primary",
                "divider": "border.subtle",
                "actionBg": "brand.primary", "actionLabel": "text.inverse"},
        states=["default", "필수 미입력(검색 비활성)"],
        usage="숙박 검색의 시작점. 지점·날짜·인원을 한 줄로. 첫 화면 바로 아래에 둠",
        dont="필드를 다섯 개 넘기지 않음. 그 이상은 상세 검색으로 넘김",
        css=f".c{{width:{lay('container.max')};display:flex;align-items:flex-end;"
            f"gap:{sz('booking.barGap')};"
            f"padding:{sz('booking.barPaddingY')} {lay('container.gutter')};"
            f"background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".f{{display:flex;flex-direction:column;gap:{sz('booking.fieldGap')};flex:1;min-width:0}}"
            f".f + .f{{border-left:{sz('border.width')} solid var(--color-border-subtle);"
            f"padding-left:{sz('booking.barGap')}}}"
            f".l{{{t('label', tokens)}color:var(--color-text-secondary)}}"
            f".v{{{t('body1-bold', tokens)}color:var(--color-text-primary);{NUM}"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}"
            f".b{{{btn_base}flex:none;height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"{t('body1-bold', tokens)}}}",
        html='<div class="c">'
             '<div class="f"><div class="l">지점</div><div class="v">전체 지점</div></div>'
             '<div class="f"><div class="l">체크인 – 체크아웃</div><div class="v">09.12 – 09.14</div></div>'
             '<div class="f"><div class="l">객실 · 인원</div><div class="v">1실 · 성인 2</div></div>'
             '<button class="b">검색</button></div>',
    )

    add(
        id="date-range-md", name="Date Range / MD", group="booking",
        tags=["예약", "날짜", "기간"], since="v1.13.0",
        spec={"width": "field.width", "height": "field.height",
              "paddingX": "field.paddingX", "radius": "md",
              "borderWidth": "border.width", "gap": "booking.fieldGap",
              "typography": "body1-bold", "nightsTypography": "caption"},
        tokens={"border": "border.default", "value": "text.primary",
                "separator": "text.tertiary",
                "nights": "brand.onSubtle", "nightsBg": "brand.subtle"},
        states=["default", "focus", "미선택"],
        usage="체크인과 체크아웃을 한 입력으로. 며칠 묵는지를 함께 보여 줌",
        dont="날짜 입력 두 개로 쪼개지 않음 — 사람은 기간 하나로 생각함",
        css=f".c{{width:{sz('field.width')};height:{sz('field.height')};"
            f"display:flex;align-items:center;gap:{sz('booking.fieldGap')};"
            f"padding:0 {sz('field.paddingX')};border-radius:var(--radius-md);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"background:var(--color-surface-default)}}"
            f".v{{{t('body1-bold', tokens)}color:var(--color-text-primary);{NUM}}}"
            f".s{{{t('body1-bold', tokens)}color:var(--color-text-tertiary)}}"
            f".n{{margin-left:auto;{t('caption', tokens)}{NUM}"
            f"padding:0 {sz('badge.paddingX')};height:{sz('badge.height')};"
            f"display:inline-flex;align-items:center;border-radius:var(--radius-full);"
            f"background:var(--color-brand-subtle);color:var(--color-brand-onSubtle)}}",
        html='<div class="c"><span class="v">09.12</span><span class="s">–</span>'
             '<span class="v">09.14</span><span class="n">2박</span></div>',
    )

    add(
        id="stepper-md", name="Stepper / MD", group="booking",
        tags=["예약", "인원", "수량"], since="v1.13.0",
        spec={"buttonSize": "booking.stepperSize",
              "valueWidth": "booking.stepperValueWidth",
              "gap": "booking.stepperGap", "radius": "sm",
              "borderWidth": "border.width", "typography": "body1-bold"},
        tokens={"border": "border.default", "icon": "text.primary",
                "value": "text.primary", "disabled": "text.disabled"},
        states=["default", "최소값(감소 비활성)", "최대값(증가 비활성)"],
        usage="객실 수·성인·어린이처럼 작은 정수를 세는 자리",
        dont="열을 넘길 수 있는 값에는 쓰지 않음. 그때는 select 로",
        css=f".c{{display:inline-flex;align-items:center;gap:{sz('booking.stepperGap')}}}"
            f".s{{{btn_base}width:{sz('booking.stepperSize')};"
            f"height:{sz('booking.stepperSize')};border-radius:var(--radius-sm);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"background:var(--color-surface-default);color:var(--color-text-primary);"
            f"{t('body1-bold', tokens)}}}"
            f".s.off{{color:var(--color-text-disabled);"
            f"border-color:var(--color-border-subtle)}}"
            f".v{{min-width:{sz('booking.stepperValueWidth')};text-align:center;"
            f"{t('body1-bold', tokens)}color:var(--color-text-primary);{NUM}}}",
        html='<div class="c"><button class="s off">−</button>'
             '<span class="v">2</span><button class="s">+</button></div>',
    )

    add(
        id="stay-summary-md", name="Stay Summary / MD", group="booking",
        tags=["예약", "요약", "투숙조건"], since="v1.13.0",
        spec={"width": "container.max", "paddingY": "booking.summaryPaddingY",
              "gap": "booking.barGap", "borderWidth": "border.width",
              "labelTypography": "caption", "valueTypography": "body1-bold"},
        tokens={"bg": "surface.subtle", "border": "border.subtle",
                "label": "text.tertiary", "value": "text.primary"},
        states=["default"],
        usage="예약 단계 상단에 고른 조건을 고정 표시. 지점·날짜·박수·인원",
        dont="여기서 값을 고치게 하지 않음. 고치려면 검색으로 되돌림",
        css=f".c{{width:{lay('container.max')};display:flex;"
            f"gap:{sz('booking.barGap')};align-items:center;"
            f"padding:{sz('booking.summaryPaddingY')} {lay('container.gutter')};"
            f"background:var(--color-surface-subtle);"
            f"border-block:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".i{{display:flex;flex-direction:column;gap:2px}}"
            f".l{{{t('caption', tokens)}color:var(--color-text-tertiary)}}"
            f".v{{{t('body1-bold', tokens)}color:var(--color-text-primary);{NUM}}}",
        html='<div class="c">'
             '<div class="i"><div class="l">지점</div><div class="v">도심 지점</div></div>'
             '<div class="i"><div class="l">체크인</div><div class="v">09.12 금</div></div>'
             '<div class="i"><div class="l">숙박</div><div class="v">2박</div></div>'
             '<div class="i"><div class="l">체크아웃</div><div class="v">09.14 일</div></div>'
             '<div class="i"><div class="l">인원</div><div class="v">1실 · 성인 2</div></div></div>',
    )

    add(
        id="price-member-md", name="Price / Member / MD", group="booking",
        tags=["예약", "가격", "회원가"], since="v1.13.0",
        spec={"gap": "booking.priceGap", "listTypography": "body2",
              "memberTypography": "heading3", "noteTypography": "caption"},
        tokens={"listLabel": "text.tertiary", "list": "text.secondary",
                "memberLabel": "text.brand", "member": "text.brand",
                "note": "text.tertiary"},
        states=["default", "회원가 없음"],
        usage="일반가와 회원가를 나란히. 회원가를 크고 굵게 둬서 가입 동기를 만듦",
        dont="회원가만 단독으로 쓰지 않음 — 비교 대상이 없으면 싼지 알 수 없음. "
             "할인율·정가 구조는 이것이 아니라 price-discount-md",
        css=f".c{{display:flex;flex-direction:column;gap:{sz('booking.priceGap')};"
            f"align-items:flex-end}}"
            f".r{{display:flex;align-items:baseline;gap:{sz('price.gap')}}}"
            f".ll{{{t('body2', tokens)}color:var(--color-text-tertiary)}}"
            f".lv{{{t('body2', tokens)}color:var(--color-text-secondary);{NUM}}}"
            f".ml{{{t('caption', tokens)}color:var(--color-text-brand)}}"
            f".mv{{{t('heading3', tokens)}color:var(--color-text-brand);{NUM}}}"
            f".n{{{t('caption', tokens)}color:var(--color-text-tertiary)}}",
        html='<div class="c">'
             '<div class="r"><span class="ll">일반가</span><span class="lv">₩ 283,000~</span></div>'
             '<div class="r"><span class="ml">회원가</span><span class="mv">₩ 254,600~</span></div>'
             '<div class="n">1박 기준 · 세금 봉사료 포함</div></div>',
    )

    add(
        id="rate-card-lg", name="Rate Card / LG", group="booking",
        tags=["예약", "요금", "상품"], since="v1.13.0",
        spec={"width": "container.max", "paddingX": "booking.ratePaddingX",
              "paddingY": "booking.ratePaddingY", "gap": "booking.rateGap",
              "radius": "xl", "borderWidth": "border.width",
              "titleTypography": "heading3", "bodyTypography": "body2",
              "actionHeight": "control.md.height"},
        tokens={"bg": "surface.default", "border": "border.subtle",
                "title": "text.primary", "body": "text.secondary",
                "actionBg": "brand.primary", "actionLabel": "text.inverse"},
        states=["default", "hover", "매진"],
        usage="요금 상품 한 줄. 상품명 · 포함 내역 · 가격 · 선택 버튼",
        dont="포함 내역을 세 줄 넘기지 않음. 나머지는 상세로 넘김",
        css=f".c{{width:{lay('container.max')};display:flex;align-items:center;"
            f"gap:{sz('booking.ratePaddingX')};"
            f"padding:{sz('booking.ratePaddingY')} {sz('booking.ratePaddingX')};"
            f"border-radius:var(--radius-xl);background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".m{{flex:1;min-width:0;display:flex;flex-direction:column;"
            f"gap:{sz('booking.rateGap')}}}"
            f".t{{{t('heading3', tokens)}color:var(--color-text-primary);{KO}}}"
            f".d{{{t('body2', tokens)}color:var(--color-text-secondary);{KO}}}"
            f".d li{{list-style:none}}"
            f".p{{flex:none;display:flex;align-items:center;"
            f"gap:{sz('booking.ratePaddingX')}}}"
            f".b{{{btn_base}height:{sz('control.md.height')};"
            f"padding:0 {sz('control.md.paddingX')};border-radius:var(--radius-md);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"{t('body2-bold', tokens)}}}"
            f".pr{{display:flex;flex-direction:column;align-items:flex-end;"
            f"gap:{sz('booking.priceGap')}}}"
            f".ll{{{t('body2', tokens)}color:var(--color-text-tertiary);{NUM}}}"
            f".mv{{{t('heading3', tokens)}color:var(--color-text-brand);{NUM}}}",
        html='<div class="c"><div class="m">'
             '<div class="t">조식 포함 · 레이트 체크아웃</div>'
             '<ul class="d"><li>조식 2인 · 오후 2시 퇴실</li>'
             '<li>투숙 3일 전까지 무료 취소</li></ul></div>'
             '<div class="p"><div class="pr">'
             '<span class="ll">일반가 ₩ 283,000~</span>'
             '<span class="mv">₩ 254,600~</span></div>'
             '<button class="b">객실 선택</button></div></div>',
    )

    add(
        id="tooltip-md", name="Tooltip / MD", group="feedback",
        tags=["툴팁", "보조설명", "규정"], since="v1.13.0",
        spec={"iconSize": "tooltip.iconSize", "paddingX": "tooltip.paddingX",
              "paddingY": "tooltip.paddingY", "maxWidth": "tooltip.maxWidth",
              "radius": "md", "typography": "caption", "elevation": 2},
        tokens={"icon": "text.tertiary", "bg": "surface.inverse",
                "label": "text.inverse"},
        states=["default", "열림"],
        usage="연령 기준·취소 규정처럼 짧은 보조 설명. 아이콘을 누르거나 포커스하면 열림",
        dont="여기에만 있는 정보를 두지 않음(§7-9). 본문으로도 알 수 있어야 함",
        css=f".c{{display:inline-flex;align-items:center;gap:{sz('chip.gap')}}}"
            f".t{{{t('body2', tokens)}color:var(--color-text-primary)}}"
            f".i{{width:{sz('tooltip.iconSize')};height:{sz('tooltip.iconSize')};"
            f"border-radius:var(--radius-full);display:inline-flex;"
            f"align-items:center;justify-content:center;"
            f"border:{sz('border.width')} solid var(--color-text-tertiary);"
            f"color:var(--color-text-tertiary);{t('caption', tokens)}}}"
            f".p{{max-width:{sz('tooltip.maxWidth')};"
            f"padding:{sz('tooltip.paddingY')} {sz('tooltip.paddingX')};"
            f"border-radius:var(--radius-md);background:var(--color-surface-inverse);"
            f"color:var(--color-text-inverse);{t('caption', tokens)}{KO}"
            f"box-shadow:var(--elevation-2)}}",
        html='<div class="c"><span class="t">어린이</span>'
             '<span class="i">i</span>'
             '<span class="p">만 12세 이하는 어린이 요금이 적용됩니다.</span></div>',
    )



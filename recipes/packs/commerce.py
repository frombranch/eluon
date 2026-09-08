# -*- coding: utf-8 -*-
"""commerce pack — 커머스 도메인 자산.

core 는 "업종이 바뀌어도 참인 것"만 담습니다(CLAUDE.md §D).
옵션 선택과 장바구니 요약은 커머스에서만 성립하는 어휘라 여기 pack 입니다.

**수량은 여기 없습니다.** 작은 정수를 세는 일은 업종이 바뀌어도 같은 물건이라
`stepper-md` 를 core 에 두고 예약과 커머스가 같이 씁니다.
치수 토큰은 tokens/pack-commerce.json 에 있습니다.
"""

RESPONSIVE = {
    "cart-summary-lg": {"md": "fill"},
}


def build(tokens, add, t, sz, lay, btn_base, KO, NUM):
    """components.build() 의 헬퍼를 그대로 받아 커머스 자산을 추가합니다."""
    # ── 커머스(commerce) ───────────────────────────────────────────
    # 탐색 → 필터 → 상세(옵션·재고) → 장바구니 → 결제 순서에서
    # 상세와 장바구니 사이가 비어 있었습니다. 그 둘을 채웁니다.

    add(
        id="option-select-md", name="Option Select / MD", group="commerce", pack="commerce",
        tags=["커머스", "옵션", "재고"], since="v1.14.0",
        spec={"groupGap": "option.groupGap", "rowGap": "option.rowGap",
              "gap": "option.gap", "height": "option.height",
              "paddingX": "option.paddingX", "radius": "sm",
              "borderWidth": "border.width",
              "labelTypography": "label", "valueTypography": "body2"},
        tokens={"label": "text.secondary", "border": "border.default",
                "value": "text.primary", "selectedBorder": "brand.primary",
                "selectedBg": "brand.subtle", "selectedLabel": "text.brand",
                "soldOut": "text.disabled"},
        states=["default", "선택됨", "품절"],
        usage="상품 옵션을 한눈에 펼쳐 고르게 함. 색상·사이즈처럼 선택지가 5개 이하일 때",
        dont="품절을 목록에서 빼지 않음 — 살 수 없다는 것도 정보임. "
             "취소선·회색만으로 품절을 알리지 않음 — 「품절」을 글자로 함께 적음. "
             "선택지가 6개를 넘으면 이것이 아니라 select-md",
        css=f".c{{display:flex;flex-direction:column;gap:{sz('option.groupGap')}}}"
            f".g{{display:flex;flex-direction:column;gap:{sz('option.rowGap')}}}"
            f".l{{{t('label', tokens)}color:var(--color-text-secondary)}}"
            f".o{{display:flex;flex-wrap:wrap;gap:{sz('option.gap')}}}"
            f".v{{display:inline-flex;align-items:center;"
            f"gap:{sz('option.gap')};"
            f"height:{sz('option.height')};padding:0 {sz('option.paddingX')};"
            f"border-radius:var(--radius-sm);"
            f"border:{sz('border.width')} solid var(--color-border-default);"
            f"background:var(--color-surface-default);"
            f"color:var(--color-text-primary);{t('body2', tokens)}}}"
            f".v.on{{border-color:var(--color-brand-primary);"
            f"background:var(--color-brand-subtle);color:var(--color-text-brand)}}"
            f".v.off{{color:var(--color-text-disabled);"
            f"border-color:var(--color-border-subtle)}}"
            f".v.off .n{{text-decoration:line-through}}"
            f".so{{{t('caption', tokens)}color:var(--color-text-disabled)}}",
        html='<div class="c">'
             '<div class="g"><div class="l">색상</div>'
             '<div class="o"><span class="v on"><span class="n">차콜</span></span>'
             '<span class="v"><span class="n">아이보리</span></span>'
             '<span class="v off"><span class="n">올리브</span>'
             '<span class="so">품절</span></span></div></div>'
             '<div class="g"><div class="l">사이즈</div>'
             '<div class="o"><span class="v"><span class="n">S</span></span>'
             '<span class="v on"><span class="n">M</span></span>'
             '<span class="v off"><span class="n">XL</span>'
             '<span class="so">품절</span></span></div></div>'
             '</div>',
    )

    add(
        id="cart-summary-lg", name="Cart Summary / LG", group="commerce", pack="commerce",
        tags=["커머스", "장바구니", "결제"], since="v1.14.0",
        spec={"width": "cart.width", "paddingX": "cart.paddingX",
              "paddingY": "cart.paddingY", "rowGap": "cart.rowGap",
              "totalGap": "cart.totalGap", "radius": "xl",
              "borderWidth": "border.width",
              "titleTypography": "heading3", "rowTypography": "body2",
              "totalTypography": "heading3",
              "actionHeight": "control.lg.height"},
        tokens={"bg": "surface.default", "border": "border.subtle",
                "title": "text.primary", "key": "text.secondary",
                "value": "text.primary", "discount": "text.brand",
                "total": "text.brand", "divider": "border.subtle",
                "actionBg": "brand.primary", "actionLabel": "text.inverse"},
        states=["default", "할인 없음", "결제 비활성(필수 동의 전)"],
        usage="장바구니·주문서에서 낼 돈을 확정하는 자리. "
              "상품 금액 · 배송비 · 할인 · 총액 순서를 바꾸지 않음",
        dont="총액을 다른 줄과 같은 활자로 두지 않음 — 어느 것이 낼 돈인지 알 수 없음. "
             "여기에만 있는 금액을 두지 않음(§7-9)",
        css=f".c{{width:{sz('cart.width')};display:flex;flex-direction:column;"
            f"gap:{sz('cart.rowGap')};"
            f"padding:{sz('cart.paddingY')} {sz('cart.paddingX')};"
            f"border-radius:var(--radius-xl);background:var(--color-surface-default);"
            f"border:{sz('border.width')} solid var(--color-border-subtle)}}"
            f".t{{{t('heading3', tokens)}color:var(--color-text-primary);{KO}}}"
            f".r{{display:flex;justify-content:space-between;align-items:baseline}}"
            f".k{{{t('body2', tokens)}color:var(--color-text-secondary)}}"
            f".v{{{t('body2', tokens)}color:var(--color-text-primary);{NUM}}}"
            f".v.dc{{color:var(--color-text-brand)}}"
            f".d{{height:{sz('border.width')};"
            f"background:var(--color-border-subtle);"
            f"margin-top:{sz('cart.totalGap')}}}"
            f".tot .k{{{t('body1-bold', tokens)}color:var(--color-text-primary)}}"
            f".tot .v{{{t('heading3', tokens)}color:var(--color-text-brand);{NUM}}}"
            f".b{{{btn_base}height:{sz('control.lg.height')};"
            f"padding:0 {sz('control.lg.paddingX')};border-radius:var(--radius-lg);"
            f"background:var(--color-brand-primary);color:var(--color-text-inverse);"
            f"{t('body1-bold', tokens)}margin-top:{sz('cart.totalGap')}}}",
        html='<div class="c">'
             '<div class="t">주문 요약</div>'
             '<div class="r"><span class="k">상품 금액</span>'
             '<span class="v">₩ 128,000</span></div>'
             '<div class="r"><span class="k">배송비</span>'
             '<span class="v">₩ 3,000</span></div>'
             '<div class="r"><span class="k">할인</span>'
             '<span class="v dc">− ₩ 12,800</span></div>'
             '<div class="d"></div>'
             '<div class="r tot"><span class="k">총 결제금액</span>'
             '<span class="v">₩ 118,200</span></div>'
             '<button class="b">결제하기</button>'
             '</div>',
    )

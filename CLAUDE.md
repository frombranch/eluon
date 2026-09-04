# ELUON — 에이전트 작업 계약서

Eluon(엘루온)은 디자인포지션의 디자인 시스템입니다.
이 파일은 사람이 아니라 **AI 에이전트가 먼저 읽는 규칙서**입니다.
이 저장소를 참조하는 모든 작업은 아래를 따릅니다.

---

## 0. 절대 규칙

1. **`manifest.json`을 읽기 전에 어떤 UI도 그리지 않는다.** 자산 ID를 추측하지 않는다.
2. **manifest에 없는 컴포넌트가 필요하면 새로 그리지 말고 보고한다.**
   `"manifest에 <x>가 없습니다. (A) 유사한 <y>로 대체 (B) 신규 제작"` — 두 안을 제시하고 사람의 결정을 기다린다.
3. **반응형은 자산마다 정해져 있다.** `manifest.json`의 **`assets[].responsiveByTheme.<테마>`**가 정답이다.
   최상위 키가 아니라 자산 안에 있고, **키는 px 숫자다** — `"768"`은 md 미만, `"480"`은 sm 미만을 가리킨다.
   `fill`(폭 100%) · `toCard`(표를 카드로) · `scrollX`(가로 스크롤) ·
   `stack`(가로 칼럼을 세로로) · `menuNav`(메뉴를 접어 토글로). 임의로 바꾸지 않는다.
   자산에 적히지 않은 구간, 즉 페이지 전체를 접는 법은 **§5 범위표**를 따른다.
   **375px에서 가로로 넘치는 요소가 없어야 한다.**

4. **`spec` 값을 임의로 바꾸지 않는다.** 높이·라운드·패딩은 manifest가 정답이다.
   이미지에서 눈대중으로 재지 않는다. 값은 이미 적혀 있다.
   ⚠️ **치수는 테마마다 다르다.** `spec`은 토큰 이름(`control.lg.height`)이고,
   실제 px는 **`specByTheme.<테마>`**에 있다. 고른 테마의 값을 읽는다.
4-1. **자산 spec 의 값이 곧 CSS 변수인 것은 아니다.** `--size-*` 는 `semantic.size` 에 있는 것뿐이다.
   자산에만 있는 항목(`header-gnb-lg.actionHeight` 같은 것)에는 대응하는 변수가 없다.
   `specByTheme` 에서 실제 값을 읽고, **같은 값을 가진 semantic 토큰을 찾아 쓴다**
   (`actionHeight` 48 → `--size-control-md-height`). 없으면 그 자산의 다른 spec 항목으로 짠다.
   ⚠️ 존재하지 않는 변수는 조용히 빈 값이 되어 높이가 무너진다. 에러가 나지 않으므로 눈으로 봐야 안다.
   실제로 `var(--size-header-actionHeight)` 를 쓴 헤더 버튼이 48px 대신 21.75px 로 찌그러졌다.
5. **색은 헥스로 쓰지 않는다.** `tokens` 필드의 시맨틱 토큰명을 CSS 변수로 선언해 쓴다.
5-1. **자산을 놓기 전에 `foundationByTheme.<테마>`를 읽는다.**
   `layout`이 폭·그리드·여백을 정하고, `typography`의 `role`이 어느 자리에 어떤 활자를 쓸지 정한다.
   글자 크기를 숫자로 쓰지 않는다 — `var(--type-heading1-size)`, 축약형 `font:var(--type-heading1)`.
   간격은 임의값을 쓰지 않는다 — `var(--space-*)`에서 고른다.
   ⚠️ 이 규칙이 생기기 전에는 규격은 맞는데 폭도 리듬도 없는 화면이 나왔다.
6. **테마를 먼저 확정한다.** `eluo`·`atlas`·`ember`·`harbor`·`tideland`·`cobalt` 중 무엇으로 만들지 모르면 물어본다. 고객사 건이면 그 고객사 테마가 있는지 `manifest.json`의 `themes`를 먼저 확인한다.
7. **`status: "deprecated"` 자산은 사용하지 않는다.** `replacedBy`를 따라간다.
7-1. **상태는 자산이 아니다.** `variantOf`가 있는 항목은 부모 자산의 상태 그림이다.
   고르는 목록에 넣지 않고, 부모의 `variants[].tokens`를 보고 **색만 바꿔서** 그린다.
   ⚠️ 에러·포커스·선택 상태를 임의로 지어내지 않는다. 무엇이 달라지는지 적혀 있다.
8. **한글 조판은 짝으로 건다.** 본문에 `word-break: keep-all`과 `overflow-wrap: anywhere`를 **함께** 건다.
   `keep-all`만 걸면 긴 영문·URL이 컨테이너를 넘치고, 그것만 걸면 한글이 낱자에서 잘린다.
   `text-wrap: pretty`로 줄 끝을 고르게 하고, 한글 사이 숫자에는 `font-variant-numeric: tabular-nums`.
   ⚠️ **줄바꿈을 `<br>`로 넣지 않는다.** 폭이 바뀌면 엉뚱한 자리에서 끊긴다. 값은 `foundationByTheme.<테마>.text`에 있다.
9. **라운드 눈금은 둘이다.** `sm`·`md`·`lg`는 컨트롤(버튼·입력·칩), **`xl`은 컨테이너**(카드·표·모달·토스트).
   섞으면 알약 버튼을 쓰는 테마에서 표와 토스트까지 알약이 된다. `build_manifest.py`가 검사한다.
10. **시간을 숫자로 쓰지 않는다.** `.4s`·`900ms` 를 쓰지 않는다.
    `var(--motion-fast|base|slow|exit)` 넷뿐이고 **280ms가 천장**이다.
    ⚠️ 이 규칙이 생기기 전에는 한 파일 안에 `.15s`·`.2s`·`.4s`·`.9s` 가 제각각 들어갔고,
    5초마다 도는 히어로의 크로스페이드가 900ms여서 매 주기의 18%가 디졸브였다. 자세히는 §6.
11. **이미지 비율과 해상도는 정해져 있다.** 비율은 `var(--media-ratio-*)` 넷 중 하나,
    요청 해상도는 표시 폭의 `--media-density`배(2배)다. 새 비율을 만들지 않는다.
    ⚠️ 이 규칙이 생기기 전에는 한 페이지에 `4/5`·`16/9`·`9/16`·`16/10` 이 섞였고,
    700px 이미지를 2배 밀도 화면에 띄워 흐릿했다. 자세히는 §8.

---

## 1. 구조

```
manifest.json              ← 단일 진실 공급원(SSOT). 항상 여기부터.
                              spec = 토큰 이름 · specByTheme = 테마별 실제 수치
                              foundationByTheme = 활자(role 포함)·레이아웃·간격·그림자
docs/eluon.json            ← [생성됨] 프롬프트 빌더가 읽는 변환본. manifest 에서 파생
docs/prompt-builder.html   ← 프롬프트 빌더. Pages 로 서빙됨
docs/guide.src.html        ← 사용설명서 본문. 사람이 씀
docs/guide.html            ← [생성됨] 사용설명서. 버전·개수는 manifest 에서 채움
tokens/core.json           ← 브랜드 중립 파운데이션
tokens/theme-eluo.json     ← ELUO 오버라이드 (고객사 테마도 이 형식으로 복제)
docs/tokens/eluon-*.css    ← [생성됨] 테마별 CSS 변수. 코드에 그대로 붙여 쓴다
recipes/components.py      ← 컴포넌트 정의. spec이 곧 CSS이고 곧 이미지다
                              RESPONSIVE 표에 자산별 접기 규칙이 한곳에 모여 있다
assets/components/         ← 렌더된 PNG(테마별) + 사이드카 JSON
index/sheet-<theme>.png    ← [생성됨] 몽타주 시트
docs/index.html            ← [생성됨] 공개 문서 사이트
prompts/                   ← 검증된 프롬프트 템플릿
```

**중요:** `manifest.json`·`docs/eluon.json`·`docs/`·`index/`·`assets/**/*.png`는 전부 생성물입니다.
사람이 고치는 것은 `tokens/`와 `recipes/components.py` 둘뿐입니다.

---

## 2. 테마

| 테마 | 무엇 | 언제 |
|---|---|---|
| `eluo` | ELUO 브랜드. Navy `#000080`, 라운드 축소 | 자사 제안·내부 산출물의 기본값 |
| `atlas` | 고객사 테마(가명). 딥 네이비 `#001F45`, radius 4 | 해당 고객사 건 |
| `ember` | 고객사 테마(가명). 딥그린 `#12503C`, 버튼 라운드 2 | 해당 고객사 건 |
| `harbor` | 고객사 테마(가명). 웜 토프 `#816C58`, 라운드 4 | 해당 고객사 건 |
| `tideland` | 고객사 테마(가명). 테라코타 `#B44E2B`, 라운드 확대 | 해당 고객사 건 — **⛔ 추정값. 대외 제출 금지** |
| `cobalt` | 고객사 테마(가명). 네이비 `#051469`, 알약 라운드 | 해당 고객사 건 |

> `core`는 **테마 목록에 없습니다.** `tokens/core.json`은 그대로 있습니다 — 모든 테마가 `extends: core`로 이 파일 위에 얹히는 파운데이션이라 지울 수 없습니다. 뺀 것은 "브랜드 없이 파운데이션만 렌더한 결과물"이고, 실제로 고를 일이 없어 혼란만 줬습니다.

> ⚠️ `ember`는 **가명이라 이름과 색이 다릅니다** — 잉걸불이라는 이름과 달리 실제 브랜드색은 딥그린 `#12503C`입니다. 브랜드색은 언제나 `--color-brand-primary`에서 읽으십시오. (이 테마 id는 한때 `amber`였는데, `core.json`의 `primitive.amber`(경고색 램프)와 이름이 겹쳐 바꿨습니다.)

### 테마마다 얼마나 믿을 수 있나

모든 고객사 테마는 `$status`를 갖습니다. 없으면 `build_manifest.py`가 실패합니다.

| 값 | 뜻 |
|---|---|
| `measured` | 색·치수 모두 실측 |
| `partial` | 색은 실측, 치수는 일부만. 안 잰 축은 우리 기본값 |
| `estimated` | **색부터 추정. 대외 제출물에 쓰지 않는다** |

`manifest.json`의 `themeStatus`에 실리고, 빌더는 `estimated` 테마를 고르면 프롬프트 맨 앞에
경고를 세웁니다. **무엇을 더 받아야 하는지는 `index/MEASURE.md`에 축별로 나옵니다** —
`scripts/build_measure.py`가 생성하며 고객사명은 들어가지 않습니다.

**고객사 테마를 만드는 법**은 컴포넌트를 건드리는 게 아닙니다.
`tokens/theme-eluo.json`을 복제해 `semantic.color`·`semantic.radius`·**`semantic.size`**·
**`semantic.layout`**·**`typography`**·**`semantic.font`**를 덮어쓰면 30개 전부가 함께 바뀝니다. **크기·패딩도 고객사 실측값을 넣습니다** — 우리는 대행사이고
테마는 곧 그 고객의 데이터입니다. 실측 기록이 없는 축은 덮어쓰지 말고 core 기본값을 두되,
무엇을 옮겼고 무엇을 안 옮겼는지 테마 파일의 `$measured`에 적습니다.

> **테마로 흡수되지 않는 것**: 채움형이냐 아웃라인형이냐 같은 **구조**는 수치가 아니라서
> 토큰으로 안 담깁니다. 그럴 때는 다른 자산을 쓰거나 새 컴포넌트를 만듭니다.

> **테마 값은 피그마가 아니라 공개 웹사이트에서도 뽑을 수 있습니다.** 브라우저의 computed style 을
> 읽으면 실제로 렌더된 값이 나옵니다. 다만 사이트가 뷰포트 비례(fluid rem) 배치면 기준 폭을 정해
> 환산해야 하는데, **그때 rem 인 값과 고정 px 인 값을 반드시 구분합니다.** 루트 폰트 크기를 두 배로
> 바꿔 다시 재면 rem 값만 두 배가 됩니다. 테두리는 보통 고정 px 라, 환산하면 1px 이 1.6 이 됩니다
> (harbor 에서 실제로 겪었습니다). 그리고 `usage`·`dont` 같은 판단은 사이트에서 알 수 없어 사람이 채워야 합니다.
> 리뉴얼 제안이면 현재 사이트가 **바꿀 대상**일 수 있으니 기준으로 삼기 전에 확인합니다.

> **실측 안 된 축은 프롬프트가 스스로 밝힙니다.** `eluon.config.json`의 `defaultTheme`이 아닌
> 테마는 전부 고객사 테마로 봅니다. 그 테마가 `semantic.size`에서 안 덮어쓴 축은
> "아직 안 잰 축"으로 판정되어, 빌더가 만드는 프롬프트 맨 앞에 **무엇이 실측이고 무엇이
> 기본값인지** 한 줄로 실립니다. 자료를 색부터 받고 치수를 나중에 받는 게 정상 순서라
> 이 구간이 반드시 생깁니다.
**`eluon.config.json`의 `themes` 배열에 추가하는 것을 잊지 마십시오** — 빠뜨리면 스크립트가 그 테마를 렌더하지 않습니다.

> `atlas`의 accent는 `coral.600 #C24D3A`입니다. 원본 브랜드 코랄 `#D85640`은 흰 텍스트 3.94:1 · 짙은 텍스트 4.38:1로 양쪽 다 AA 미달이라, 텍스트를 얹는 면에는 쓰지 않습니다.

> ELUO의 accent `#FFFF01`은 면적 강조에만 씁니다. 흰 배경 위 텍스트 색으로 쓰면 대비비 1.07:1로 전혀 읽히지 않습니다.

---

## 3. 자산을 쓰는 3가지 경로

### 경로 A — 코드로 재현 (권장, 결과물이 살아있는 UI일 때)
이미지를 붙이지 말고 **토큰 CSS + spec으로 실제 컴포넌트를 만듭니다.**

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/frombranch/eluon@v1.12.2/docs/tokens/eluon-eluo.css">
<style>
.btn-primary-lg{
  height:56px; padding:0 24px; border-radius:var(--radius-lg);
  background:var(--color-brand-primary); color:var(--color-text-inverse);
  font-size:16px; font-weight:700;   /* body1-bold */
}
</style>
```

수치는 manifest의 `spec`에서, 색은 `tokens`에서 그대로 가져옵니다.

### 경로 B — 이미지 URL 참조 (목업·와이어프레임)
manifest의 `cdn.<theme>` 값을 그대로 `<img src>`에 씁니다. 손으로 URL을 조립하지 않습니다.
⚠️ **클로드 아티팩트로 발행할 페이지에는 외부 이미지가 차단됩니다.** 그 경우 경로 C.

### 경로 C — 저장소 클론 (시각 검수·인라인)
```bash
git clone --depth 1 --branch v1.12.2 https://github.com/frombranch/eluon.git
```
이미지를 실제로 봐야 할 때, 또는 base64로 인라인해야 할 때만.

### 몽타주 시트
`index/sheet-eluo.png` 한 장에 36개가 라벨과 함께 들어 있습니다. 상태 변형 5개는 빠져 있습니다 — 고르는 물건이 아닙니다.
"이 중에 골라줘" 단계에서는 개별 이미지 대신 이 시트를 첨부합니다.

---

## 4. 작업 유형별 절차

**사이트에서 자산 후보 찾기**
1. 주소를 열어 computed style 로 반복되는 UI 조각을 재고 **반복 횟수**를 센다
2. `manifest.json`과 대조해 표 두 개로 — 이미 있는 것 / 없는 것
3. **발견까지만.** 레시피는 쓰지 않는다. 만들려면 아래 "신규 컴포넌트 추가"로 넘어간다.
> 한 번만 나오는 요소는 자산이 아니라 그 화면 전용입니다. 반복 횟수가 판단 근거입니다.

**시안 제작**
1. `manifest.json` 읽기 → 2. 테마 확인 → 3. **쓸 자산 ID 목록을 먼저 보고**
→ 4. 승인 후 조립 → 5. 사용한 ID 목록을 결과 하단에 명시

**일관성 QA**
1. **먼저 테마를 확정한다.** 치수가 테마마다 다르므로 어느 테마 기준인지 없이는 대조가 성립하지 않는다.
2. 대상과 manifest의 **`specByTheme.<테마>`**를 항목별로 대조 (`spec`은 토큰 이름이라 대조 대상이 아니다)
3. **반응형도 대조한다.** `assets[].responsiveByTheme.<테마>`와 실제 동작, §5 범위표(특히 768–1023 태블릿),
   그리고 375px 가로 넘침
3-1. **모션과 이미지도 대조한다.** 시간 리터럴(`.4s` 같은 것)이 남아 있는지, 비율이 `--media-ratio-*` 밖의
   값인지, 자동 재생에 멈춤 버튼이 있는지. §6·§8이 기준이다.
4. `자산ID / 기대값 / 실제값 / 위치 / 심각도` 표로 보고
5. **자동 수정하지 않는다.** 표만 낸다.

### 페이지를 이루는 덩어리

원자만 있고 판이 없으면 화면마다 헤더·히어로·푸터를 새로 그리게 됩니다. `layout` 그룹이 그 자리입니다.

| 자산 | 무엇 |
|---|---|
| `header-gnb-lg` | 로고 · 주 메뉴 · 주요 액션 |
| `hero-split-lg` | 첫 화면. 제목·리드·액션 + 지표 레일 |
| `section-header-md` | 섹션 머리. 아이브로우 · 제목 · 리드 |
| `cta-band-lg` | 전환 유도 띠. 한 페이지에 하나 |
| `list-row-md` | 제목·메타·값 한 줄 목록 |
| `form-field-md` | 라벨 · 입력 · 도움말 묶음 |
| `footer-lg` | 로고 · 고지 · 보조 메뉴 |

이 덩어리들은 콘텐츠 폭 자체가 규격이라 `spec.width`가 `container.max`를 가리킵니다 — 크기 토큰이 아니라 `semantic.layout` 값입니다.

### 아이콘

아이콘은 자산으로 렌더하지 않습니다. 화면을 만들 때 **Lucide** 에서 가져다 쓰고, 이 규칙을 지킵니다.

| 항목 | 값 | 토큰 |
|---|---|---|
| 출처 | Lucide 한 세트만 | `semantic.icon.source` |
| 크기 | 24×24 기준, 2의 배수(24 · 48) | `--size-icon-md` · `--size-icon-lg` |
| 스타일 | 채우지 않음(`fill:none`), 선만 | `--icon-fill` |
| 선 굵기 | 1.2 (Lucide 기본 2 는 무겁습니다) | `--icon-strokewidth` |
| 불투명도 | 0.7 | `--icon-opacity` |
| 색 | `currentColor` — 부모 색을 따라 테마와 함께 바뀜 | `--icon-stroke` |

```html
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
<style>[data-lucide]{fill:none;stroke:currentColor;stroke-width:1.2;opacity:.7}</style>
<i data-lucide="arrow-right" width="24" height="24"></i>
<script>lucide.createIcons();</script>
```

채운 아이콘(버튼처럼 면으로 찬 것)은 쓰지 않습니다. 아이콘이 글자보다 앞으로 나오면
옆의 문장이 안 읽힙니다.

### 상태를 다루는 법

`btn-primary-lg-disabled` 같은 항목은 **자산이 아니라 `btn-primary-lg`의 상태 그림**입니다.
`variantOf`로 부모에 매달려 있어 자산 수(31)에 세지 않고, 몽타주 시트와 빌더 목록에도 나오지 않습니다.

```json
"btn-primary-lg": {
  "states": ["default","hover","pressed","disabled"],
  "variants": [{"id":"btn-primary-lg-disabled","state":"disabled",
                "tokens":{"bg":"surface.disabled","label":"text.disabled"}}]
}
```

규격은 부모와 같고 **토큰만 다릅니다.** 상태를 그릴 때는 부모 spec에 이 토큰만 얹습니다.
이미지가 필요하면 변형의 `cdn` URL이 그대로 있습니다.

**신규 컴포넌트 추가**
이미지를 만들어 넣는 게 아니라 `recipes/components.py`에 dict를 추가하고 파이프라인을 돌립니다.
```bash
python3 scripts/build_tokens.py && python3 scripts/render.py \
  && python3 scripts/build_manifest.py && python3 scripts/build_pb_manifest.py \
  && python3 scripts/make_montage.py && python3 scripts/build_measure.py \
  && python3 scripts/build_docs.py && python3 scripts/build_guide.py
```

---

## 5. 반응형 범위 (테마 무관)

자산에 적힌 `responsiveByTheme`가 **그 자산**을 접는 법이라면, 이 표는 **페이지 전체**를 접는 법이다.
여섯 테마의 값이 전부 같으므로 테마별로 나누지 않는다.

키는 전부 **max-width 하향식**이다. `min-width` 미디어쿼리는 이 시스템에 없다.
`sm`=480 · `md`=768 · `lg`=1024이고, `responsiveByTheme`의 px 키가 그 숫자다.

| 축 | ≥1024 데스크톱 | 768–1023 태블릿 | 480–767 | <480 모바일 |
|---|---|---|---|---|
| 컨테이너 | `container.max` 가운데 | 100% | 100% | 100% |
| 좌우 거터 | `container.gutter` | `container.gutter` | `container.gutterMd` | `container.gutterSm` |
| 12열 격자 | 설계대로 (7/5 · 6/6) | 6/6 또는 전폭 | 전폭 1열 | 전폭 1열 |
| 카드 그리드 | 3–4열 | **2열** | 2열 | 1열 |
| 섹션 상하 | `section.padY` | `section.padY` | `section.padYMd` | `section.padYSm` |
| 내비 | 가로 GNB | 가로 GNB | `menuNav` | `menuNav` |
| 활자 | 그대로 | 그대로 | 그대로 | display1·heading1 한 칸 내려 |
| 누를 수 있는 것 | ≥24px | ≥24px | ≥`size.touch.min` | ≥`size.touch.min` |
| `*-lg` 버튼 | 내용 폭 | 내용 폭 | 폭 100% | 폭 100% |

**활자 한 칸 내리기** — 480 미만에서 `display1`은 `heading1` 크기를, `heading1`은 `heading2` 크기를 쓴다.
**역할은 그대로다.** 여전히 그 화면의 제목이다. 새 숫자를 만드는 게 아니라 있는 토큰을 옮겨 쓰는 것이므로
§0-5-1의 "글자 크기를 숫자로 쓰지 않는다"와 어긋나지 않는다.
본문(`body1`·`body2`)은 어느 폭에서도 바뀌지 않는다.

**누를 수 있는 것이 44보다 작을 때** — `pagination.itemSize` 40 · `toggle.size` 40 · `chip.height` 36 ·
`control.sm.height` 36은 전부 44 미만이다. §0-4가 `spec` 변경을 금지하므로
**시각 치수는 그대로 두고 히트 영역만 넓힌다.**

```css
position:relative;
::after{content:'';position:absolute;inset:50% 50%;
  width:var(--size-touch-min);height:var(--size-touch-min);
  transform:translate(-50%,-50%)}
```

**절대 일어나지 않아야 할 것**

- 375px에서 가로 스크롤
- 뷰포트보다 큰 고정 px 폭. 격자 자식에 `min-width:0`, 이미지에 `max-width:100%`
- 본문 16px 미만
- `min-width` 미디어쿼리. 하향식 하나로만 쓴다 — 섞으면 두 규칙이 겹치는 구간이 생긴다
- ⚠️ **768–1023을 손대지 않고 넘어가는 것.** 실제로 브레이크포인트가 767·479 둘뿐인 시안이 나왔고,
  1023px에서 4열 카드의 폭이 225px로 줄어 카드 발치의 배지와 버튼이 줄바꿈되며 무너졌다.
  고객은 제안서를 아이패드로 연다.

---

## 6. 모션 (테마 무관)

1. **모션은 사람의 행동에 대한 대답이다.** hover · focus · press · 상태를 바꾸는 클릭에만 건다.
2. **시간을 숫자로 쓰지 않는다.** 축약형 다섯 중에서 고른다 —
   반응은 `var(--motion-fast|base|slow|exit)`, 등장은 `var(--motion-entrance)`,
   사진 확대는 `var(--motion-zoom)`.
   **반응은 280ms가 천장이다.** 사람이 누른 것에 대한 대답은 빨라야 한다.
   천장은 **대답에만** 걸린다 — 등장과 사진 확대는 대답이 아니라 분위기라 느려도 된다.
   **등장(`--motion-entrance` 420ms)만 그보다 길다.** 처음 나타나는 것은 여유가 있어야 눈에 밟힌다.
   이 둘을 섞지 않는다 — hover 에 `--motion-entrance` 를 쓰면 굼떠 보이고,
   등장에 `--motion-fast` 를 쓰면 나타난 줄도 모른다.
3. **움직일 수 있는 속성은 다섯뿐.** `opacity` · `transform` · `background-color` · `border-color` · `color`.
   `height` · `width` · `top/left` · `box-shadow` · `filter`는 애니메이션하지 않는다. 레이아웃이 흔들린다.
4. **어디에 무엇을 쓰나**

   | 무엇 | 토큰 |
   |---|---|
   | 버튼·링크·칩·입력의 hover/press/focus 색·테두리 | `--motion-fast` |
   | 열고 닫기 — 아코디언 아이콘, 메뉴 토글, 탭 인디케이터 | `--motion-base` |
   | 화면을 덮는 것 — 모달·토스트 등장, 전면 이미지 전환 | `--motion-slow` |
   | 사라지는 것 — 모달·토스트 퇴장 | `--motion-exit` |
   | 사진 hover 확대 | `--motion-zoom` + `--motion-scale-hover` |
   | 스크롤 진입 등장 | `--motion-entrance` + `--motion-distance-reveal` |

   `transition`은 `:hover` 규칙이 아니라 **기본 상태에** 건다. 그래야 돌아올 때도 같은 속도다.
5. **사진 hover 확대 — 규격대로 쓴다.** 흔히 기대하는 움직임이라 금지하지 않는다. 대신 규격이 있다.

   | 항목 | 값 |
   |---|---|
   | 배율 | `var(--motion-scale-hover)` (1.03). 더 키우지 않는다 |
   | 시간 | `var(--motion-zoom)` (520ms). **반응이 아니라 은근한 움직임이라 느리다** |
   | 거는 대상 | **사진에만.** 카드 전체를 키우지 않는다 — 옆 카드와 간격이 흔들린다 |
   | 자르기 | 부모에 `overflow:hidden`. 사진이 틀 밖으로 나오지 않는다 |
   | 조건 | **감싼 요소가 링크·버튼일 때만**(§7-9). 아무 데도 안 가는 카드는 반응하지 않는다 |

   `transform:scale()` 만 쓴다. `width`·`height` 로 키우면 레이아웃이 밀린다(§6-3).
   ⚠️ 링크가 없는 `<article>` 카드에 hover 확대가 걸린 시안이 나왔다. iOS 의 sticky `:hover` 때문에
   탭한 뒤 확대된 채로 남았다.

5-1. **스크롤 진입 등장 — 규격대로 쓴다.** 이것도 금지하지 않는다.

   | 항목 | 값 |
   |---|---|
   | 무엇이 움직이나 | `opacity` 0→1 과 `translateY(var(--motion-distance-reveal))` (16px). 둘뿐이다 |
   | 시간·커브 | `var(--motion-entrance)` |
   | 몇 번 | **한 번.** `IntersectionObserver` 로 한 번 보이면 관찰을 끊는다. 되감기지 않는다 |
   | 단위 | **섹션 단위.** 문단·글자마다 걸지 않는다 |
   | 시차 | 한 섹션 안에서 나란한 것들만 `var(--motion-stagger)`(60ms) 씩. **최대 4개까지** |
   | 첫 화면 | **히어로에는 걸지 않는다.** 처음 보이는 것이 늦게 나타나면 느린 사이트로 읽힌다 |

   ⚠️ **JS 가 죽어도 내용은 보여야 한다.** 숨기는 클래스를 HTML 에 박지 말고 JS 가 붙인다.
   `document.documentElement.classList.add('reveal-ready')` 를 먼저 하고 CSS 는 그 안에서만 숨긴다.
   그래야 스크립트가 실패해도 빈 페이지가 되지 않는다.
   감속 설정에서는 토큰 CSS 가 거리를 0 으로, 시간을 1ms 로 만들어 **자동으로 그냥 나타난다.**

5-2. **그래도 넣지 않는 것.** 페이지 로드 시퀀스(요소들이 차례로 튀어나오는 것), 패럴랙스,
   숫자 카운트업, 타이핑 효과, 무한 마퀴, 장식용 `@keyframes`, 커서를 따라다니는 것.
   ⚠️ 5·5-1 은 **규격 안에서만** 허용이다. 배율을 1.08 로 올리고 문단마다 페이드를 걸면
   그때부터는 기계가 만든 화면으로 읽힌다. 값은 토큰에 있고 토큰을 바꾸지 않는다.
6. **자동 재생은 조건부로만 허용한다.** 셋을 다 갖추지 않으면 쓰지 않는다.
   1. 멈춤 버튼. **`mouseenter`로 멈추는 것은 터치에서 아예 동작하지 않으므로 이를 대신하지 못한다**
   2. `matchMedia('(prefers-reduced-motion: reduce)').matches`면 시작하지 않는다
   3. 탭이 가려지면(`document.hidden`) 멈춘다

   셋이 갖춰졌을 때, 사람이 건드리지 않아도 움직이는 것은 **화면당 하나**까지다.
   ⚠️ 히어로 슬라이드가 `mouseenter`로만 멈추는 시안이 나왔다. 터치에서는 멈출 방법이 없어
   페이지에서 가장 큰 요소가 WCAG 2.2.2 위반이었다.
7. **`prefers-reduced-motion`은 토큰 CSS가 이미 처리한다.** 시안에 그 `@media`를 따로 쓰지 않는다.
   단 하나, **JS 자동 재생은 CSS가 못 막는다** — 6번이 그 자리다.
8. **사람이 건드려서 움직이는 것에는 제한이 없다.**
   이 장은 움직임의 총량을 줄이려는 게 아니라, 그 움직임이 무엇에 대한 대답인지를 묻는다.
9. **움직일 것이 있어야 움직인다.** 규칙을 다 지켜도 화면이 정적으로 짜였으면 정적으로 나온다.
   탭·필터 칩·아코디언·모달·토스트가 라이브러리에 있다. 한 화면을 짤 때 **누를 것이 무엇인지**
   먼저 정한다.
   ⚠️ 실제로 자산 규격을 다 지키고도 칩 0개·탭 0개·모달 0개인 시안이 나왔다.
   모션 규칙이 아니라 화면 구성이 문제였다.

---

## 7. 좋은 화면의 최소 기준 (테마 무관)

이 장은 금지가 아니라 기준이다. 규격만 맞고 허전한 화면이 나오지 않게 한다.

1. **한 화면에 주장은 하나.** 이 페이지가 무엇을 시키는지 한 문장으로 말할 수 없으면 섹션을 지운다.
   `display1`도 주 CTA(`cta-band-lg`)도 페이지에 하나뿐이다.
2. **훑는 순서를 만든다.** 섹션은 제목 → 리드 → 내용 → (있으면) 액션 하나.
   **제목만 이어 읽어도** 페이지가 무슨 말을 하는지 알 수 있어야 한다.
3. **아이브로우는 페이지에 최대 두 개.** 모든 섹션 머리에 대문자 라벨을 얹으면 위계가 아니라 무늬가 된다.
4. **리듬은 두 값뿐.** 섹션 사이는 `section.padY`, 섹션 안 덩어리 사이는 `block.gap`.
   섹션마다 여백을 다르게 주지 않는다. 더 나눠야 하면 여백이 아니라 hairline(`border.subtle`) 하나로 나눈다.
5. **경계는 셋 중 하나만.** 한 요소에 테두리·배경·그림자를 동시에 쓰지 않는다.
   카드가 테두리를 가졌으면 `elevation`은 0이다.
6. **실제 콘텐츠로 짠다.** 제목이 두 줄인 경우, 목록이 1개인 경우와 12개인 경우를 다 확인한다.
   "제목입니다"·lorem으로 채우지 않는다.
7. **빈 상태를 함께 낸다.** 목록·표·검색이 있는 화면은 `empty-state-md`로 0건 화면을 같이 만든다.
   빈 화면은 사과문이 아니라 다음 행동이다 — "조건을 지우고 전체 보기".
8. **긴 값은 자르지 말고 흘린다.** 한글 제목에 `white-space:nowrap` + 말줄임을 쓰지 않는다.
   두 줄까지 허용(`-webkit-line-clamp:2`)하고 그 이상만 자른다. 한 줄 고정은 숫자·날짜·금액에만.
   폭 제한은 자산의 `leadMaxWidth` 같은 spec 값이 있으면 그것을, 없으면 `var(--layout-text-measure)`를 쓴다.
   ⚠️ 실제로 한글 공지 제목에 `nowrap`과 `max-width:44ch`가 걸려 제목이 통째로 잘렸다.
   `44ch`·`52ch`는 spec 에 없는 값이었다. **spec 에 없는 `ch` 숫자를 새로 만들지 않는다.**
   (`hero-split-lg`의 `60ch`, `section-header-md`의 `58ch`는 spec 값이니 그대로 쓴다.)
9. **hover로만 알 수 있는 정보를 만들지 않는다.** 터치에는 hover가 없다.
   클릭 가능한 것은 hover 없이도 클릭 가능해 보여야 한다. hover는 이미 보이는 것을 밝히는 데만 쓴다.
   **클릭할 수 없는 요소에는 hover 효과를 걸지 않는다.**
   ⚠️ 그래서 한 화면 안에서 어떤 사진은 커지고 어떤 사진은 가만히 있으면 **일관성 없어 보인다.**
   답은 hover 를 빼는 게 아니라 **그 카드를 누를 수 있게 만드는 것**이다.
   나란히 놓인 같은 종류의 카드는 전부 링크이거나 전부 아니어야 한다.
   ⚠️ 링크가 없는 `<article>` 카드에 hover 확대가 걸린 시안이 나왔다. 아무 데도 가지 않는 카드가 반응했고,
   iOS의 sticky `:hover` 때문에 탭한 뒤 확대된 채로 남았다.
10. **포커스를 지우지 않는다.** `outline:none` 금지.
    `:focus-visible`에 `var(--size-focusRing-width)` · `var(--color-focusRing)`.
    `overflow:hidden` 안의 포커스 대상은 링이 잘리므로 `outline-offset`을 음수로 주거나 클리핑을 푼다.
    sticky 헤더가 있으면 앵커 대상에 `scroll-margin-top`을 헤더 높이만큼 준다.
    페이지 맨 앞에 본문 바로가기 링크를 둔다.
11. **사진 위 글자는 판을 깐다.** 요소 전체에 `opacity`를 걸지 않는다 — 글자까지 흐려져 대비를 계산할 수 없다.
    `var(--media-scrim)`을 깔고 글자는 100%로 둔다(§8-5).
12. **효과를 넣기 전에 그게 무엇을 알려주는지 답한다.** 답이 "예뻐서"면 넣지 않는다.
    이 시스템의 인상은 여백·활자·hairline에서 나온다.
    그라디언트·글라스·블러·장식 도형·아이콘 배경 원은 쓰지 않는다.

---

## 8. 이미지 (테마 무관)

자산 규격이 다 맞아도 사진이 흐릿하거나 비율이 제각각이면 시안은 싸 보인다.
고급스러움은 사진의 내용이 아니라 **선명도 · 비율의 반복 · 글자와의 관계**에서 나온다.

1. **비율은 `var(--media-ratio-*)` 넷 중 하나.** 새 비율을 만들지 않는다.
   `wide`(16/9) 썸네일·배너 · `photo`(3/2) 일반 사진 · `portrait`(4/5) 카드 · `tall`(9/16) 전면 세로.
   한 페이지에서 같은 역할의 이미지는 같은 비율을 쓴다. **비율의 반복이 정돈된 인상을 만든다.**
2. **표시 폭의 `--media-density`배(2배)로 요청한다.** CSS상 400px로 보일 이미지는 `w=800`이다.
   가능하면 `srcset`으로 1x·2x를 함께 준다.
   ⚠️ **흐릿한 사진이 시안을 가장 빨리 싸게 만든다.** 700px 이미지를 2배 밀도 화면에 띄운 시안이 나왔다.
3. **자리를 먼저 잡는다.** 모든 `<img>`에 `width`·`height` 속성을 주거나,
   부모에 `aspect-ratio` + `object-fit:cover`를 준다. 이미지가 들어올 때 레이아웃이 밀리면 안 된다.
4. **첫 화면 이미지에는 `loading`을 걸지 않고 `fetchpriority="high"`를 준다.**
   나머지는 `loading="lazy" decoding="async"`.
5. **사진 위 글자는 `var(--media-scrim)`을 깐다.** 요소 전체에 `opacity`를 걸지 않는다.
   스크림은 평평한 검정이 아니라 아래에서 위로 옅어지는 그라디언트다 —
   글자 자리는 덮고 사진 위쪽은 그대로 둔다. 글자는 100%로 둔다.
6. **로딩 전 배경은 `surface.sunken`.** 흰 깜빡임을 만들지 않는다.
7. **미디어의 모서리는 그것을 감싼 카드와 같은 값이다.** 카드가 `radius.xl`이면 썸네일도 `radius.xl`,
   카드에 라운드가 없으면 썸네일에도 없다.
   미디어 전용 라운드 토큰은 두지 않는다 — 두 값이 어긋날 자유가 생긴다.
8. **한 페이지 안에서 톤을 섞지 않는다.** 밝은 실내 사진과 어두운 야경을 나란히 두지 않는다.
   범용 이미지를 고를 때 조도·시간대·색온도를 검색어에 함께 넣어 한 벌로 고른다.
9. **`object-position`.** 기본은 `center`. 인물·건물은 위쪽이 중요하므로 `top` 쪽으로 준다.
   얼굴이나 간판이 잘리는 크롭을 그대로 두지 않는다.
10. **`alt`.** 장식이면 빈 문자열, 정보면 무엇이 보이는지 쓴다. "이미지"·"사진" 같은 말은 쓰지 않는다.
11. **범용 이미지는 시안임을 밝힌다.** 결과 하단에 출처와 "납품 시 교체 필요"를 한 줄로 적는다.
    고객사 실제 이미지를 이 저장소에 넣지 않는다(§9).

---

## 9. 하지 않을 것

- manifest에 없는 색·폰트·라운드를 "보기 좋아서" 도입
- 생성물(`manifest.json`, `docs/`, `index/`, PNG)을 직접 편집
- 고객사 로고·실제 콘텐츠 이미지를 이 저장소에 추가 (public이다. 고객사 자산은 private 저장소로)
- 사람의 승인 없이 `tokens/`나 `recipes/` 수정

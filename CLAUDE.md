# ELUON — 에이전트 작업 계약서

Eluon(엘루온)은 디자인포지션의 디자인 시스템입니다.
이 파일은 사람이 아니라 **AI 에이전트가 먼저 읽는 규칙서**입니다.
이 저장소를 참조하는 모든 작업은 아래를 따릅니다.

---

## 0. 절대 규칙

1. **`manifest.json`을 읽기 전에 어떤 UI도 그리지 않는다.** 자산 ID를 추측하지 않는다.
2. **manifest에 없는 컴포넌트가 필요하면 새로 그리지 말고 보고한다.**
   `"manifest에 <x>가 없습니다. (A) 유사한 <y>로 대체 (B) 신규 제작"` — 두 안을 제시하고 사람의 결정을 기다린다.
3. **반응형은 자산마다 정해져 있다.** `manifest.json`의 `responsiveByTheme.<테마>`가 정답이다.
   `fill`(폭 100%) · `toCard`(표를 카드로) · `scrollX`(가로 스크롤) ·
   `stack`(가로 칼럼을 세로로) · `menuNav`(메뉴를 접어 토글로). 임의로 바꾸지 않는다.
   여러 열 그리드는 md 미만 2열 · sm 미만 1열. **375px에서 가로로 넘치는 요소가 없어야 한다.**

4. **`spec` 값을 임의로 바꾸지 않는다.** 높이·라운드·패딩은 manifest가 정답이다.
   이미지에서 눈대중으로 재지 않는다. 값은 이미 적혀 있다.
   ⚠️ **치수는 테마마다 다르다.** `spec`은 토큰 이름(`control.lg.height`)이고,
   실제 px는 **`specByTheme.<테마>`**에 있다. 고른 테마의 값을 읽는다.
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

> `core`는 v1.11.2에서 **테마 목록에서 뺐습니다.** `tokens/core.json`은 그대로 있습니다 — 모든 테마가 `extends: core`로 이 파일 위에 얹히는 파운데이션이라 지울 수 없습니다. 뺀 것은 "브랜드 없이 파운데이션만 렌더한 결과물"이고, 실제로 고를 일이 없어 혼란만 줬습니다.

> ⚠️ `ember`는 **가명이라 이름과 색이 다릅니다** — 잉걸불이라는 이름과 달리 실제 브랜드색은 딥그린 `#12503C`입니다. 브랜드색은 언제나 `--color-brand-primary`에서 읽으십시오. (v1.11.2에서는 이 테마 id가 `amber`였는데, `core.json`의 `primitive.amber`(경고색 램프)와 이름이 겹쳐 v1.11.2에서 바꿨습니다.)

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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/frombranch/eluon@v1.11.2/docs/tokens/eluon-eluo.css">
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
git clone --depth 1 --branch v1.11.2 https://github.com/frombranch/eluon.git
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
3. **반응형도 대조한다.** `responsiveByTheme.<테마>`와 실제 동작, 그리고 375px 가로 넘침
4. `자산ID / 기대값 / 실제값 / 위치 / 심각도` 표로 보고
5. **자동 수정하지 않는다.** 표만 낸다.

### 페이지를 이루는 덩어리 (v1.11.2)

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
| 크기 | 32×32 기준, 2의 배수(32 · 64) | `--size-icon-md` · `--size-icon-lg` |
| 스타일 | 채우지 않음(`fill:none`), 선만 | `--icon-fill` |
| 선 굵기 | 1.2 (Lucide 기본 2 는 무겁습니다) | `--icon-strokewidth` |
| 불투명도 | 0.7 | `--icon-opacity` |
| 색 | `currentColor` — 부모 색을 따라 테마와 함께 바뀜 | `--icon-stroke` |

```html
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
<style>[data-lucide]{fill:none;stroke:currentColor;stroke-width:1.2;opacity:.7}</style>
<i data-lucide="arrow-right" width="32" height="32"></i>
<script>lucide.createIcons();</script>
```

채운 아이콘(버튼처럼 면으로 찬 것)은 쓰지 않습니다. 아이콘이 글자보다 앞으로 나오면
옆의 문장이 안 읽힙니다.

### 상태를 다루는 법 (v1.11.2)

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

## 5. 하지 않을 것

- manifest에 없는 색·폰트·라운드를 "보기 좋아서" 도입
- 생성물(`manifest.json`, `docs/`, `index/`, PNG)을 직접 편집
- 고객사 로고·실제 콘텐츠 이미지를 이 저장소에 추가 (public이다. 고객사 자산은 private 저장소로)
- 사람의 승인 없이 `tokens/`나 `recipes/` 수정

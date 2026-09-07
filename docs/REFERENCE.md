# 참조표

`CLAUDE.md` 본문에서 빼낸 조회용 표입니다. 규칙이 아니라 **찾아보는 것**이라
작업 중 필요할 때만 엽니다. 규칙은 `CLAUDE.md`, 실패 사례는 `FAILURES.md` 입니다.

---

## 자산 카탈로그

### 페이지를 이루는 덩어리

`header-gnb-lg`(로고·주 메뉴·주요 액션) · `hero-split-lg`(제목·리드·액션 + 지표 레일, **사진 없음**) ·
`hero-media-lg`(전면 사진 위에 제목·리드·액션, 스크림 필수) · `section-header-md` ·
`cta-band-lg`(페이지에 하나) · `list-row-md` · `form-field-md` · `footer-lg`.

이 덩어리들은 콘텐츠 폭 자체가 규격이라 `spec.width` 가 `container.max` 를 가리킨다.

> **히어로는 둘 중 하나만 쓴다.** 수치를 앞세우면 `hero-split-lg`, 장소·사진을 앞세우면 `hero-media-lg`.
> 둘을 같이 놓지 않고, `hero-split-lg` 밑에 사진을 덧붙이지도 않는다.

### 페이지의 뼈대 순서

```
header-gnb-lg → 히어로 → 본문 섹션들 → cta-band-lg → footer-lg
```

**히어로는 GNB 바로 다음이다.** 검색 바·필터·예약 위젯 같은 **도구는 히어로 위가 아니라 아래**에 둔다.
사람은 "여기가 어디인지" 먼저 알고 나서 조작한다.
**브리프의 섹션 나열 순서를 배치 순서로 읽지 않는다**(`FAILURES.md#brief-order`).

### 아이콘

**Lucide** 한 세트만. 24×24 기준(2의 배수) · `fill:none` 선만 · 선 굵기 **1.2** ·
불투명도 0.7 · 색은 `currentColor`. 채운 아이콘은 쓰지 않는다.

```html
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
<style>[data-lucide]{fill:none;stroke:currentColor;stroke-width:1.2;opacity:.7}</style>
```

---

## 구조 · 경로 · 빌드

```
manifest.json          ← 단일 진실 공급원. 항상 여기부터
                          spec = 토큰 이름 · specByTheme = 테마별 실제 수치
tokens/core.json       ← 브랜드·업종 중립 파운데이션
tokens/theme-*.json    ← 고객사 값
recipes/components.py  ← 컴포넌트 정의. spec 이 곧 CSS 이고 곧 이미지다
docs/tokens/*.css      ← [생성됨] 테마별 CSS 변수
index/sheet-*.png      ← [생성됨] 엘루온 시트
```

**사람이 고치는 것은 `tokens/` 와 `recipes/` 둘뿐이다.** 나머지는 전부 생성물이다.

**자산을 쓰는 3가지 경로** — **A 코드로 재현**(권장): 토큰 CSS 링크 + spec 으로 실제 컴포넌트를 만든다.
**B 이미지 URL 참조**(목업): `cdn.<theme>` 값을 그대로 `<img src>` 에. 손으로 URL 을 조립하지 않는다.
**C 저장소 클론**(단일 파일): 토큰 CSS 를 `<style>` 에 통째로, 이미지는 base64 로.

**신규 컴포넌트 추가** — `recipes/components.py` 에 dict 를 더하고 파이프라인을 돌린다.

```bash
python3 scripts/build_tokens.py && python3 scripts/render.py \
  && python3 scripts/build_manifest.py && python3 scripts/build_pb_manifest.py \
  && python3 scripts/make_montage.py && python3 scripts/build_measure.py \
  && python3 scripts/build_docs.py && python3 scripts/build_guide.py
```

⚠️ 그룹을 추가하면 고쳐야 할 곳이 **다섯 곳**이다(`FAILURES.md#group-enum`).
⚠️ 버전을 올리면 **수기 문서 넷**도 같이 고친다(`FAILURES.md#version-bump`).

**일관성 QA** — 테마를 먼저 확정하고 `specByTheme.<테마>` 와 항목별로 대조한다.
반응형·모션·이미지도 대조한다. `자산ID / 기대값 / 실제값 / 위치 / 심각도` 표로 보고하고,
**자동 수정하지 않는다. 표만 낸다.**

---


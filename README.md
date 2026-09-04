# ELUON — 엘루온

디자인포지션의 디자인 시스템.
**사람이 보기 좋은 라이브러리가 아니라, AI 에이전트가 읽고 조립할 수 있는 라이브러리**입니다.

- 문서 사이트 → https://frombranch.github.io/eluon/
- 에이전트 규칙 → [`CLAUDE.md`](./CLAUDE.md) *(클로드는 항상 여기부터 읽습니다)*
- 자산 목록 → [`index/ASSETS.md`](./index/ASSETS.md)
- 몽타주 시트 → [`index/sheet-eluo.png`](./index/sheet-eluo.png)

컴포넌트 30개 · 테마 6종(ELUO / 아틀라스 / 엠버 / 하버 / 타이드랜드 / 코발트) · v1.11.1

---

## 30초 사용법

```
https://github.com/frombranch/eluon 의 CLAUDE.md 와 manifest.json 을 읽고,
거기 있는 자산으로만 <화면 이름> 시안을 만들어줘.
테마는 eluo 를 쓰고, 쓸 자산 ID 목록을 먼저 보여준 뒤 내 승인을 받고 조립해.
```

더 정교한 형태는 [`prompts/`](./prompts)에.

**직접 쓰기 번거로우면 프롬프트 빌더를 쓰세요.**
조건을 고르면 위 문장이 자산 계약을 지키는 형태로 완성됩니다.

→ **https://frombranch.github.io/eluon/prompt-builder.html**

열면 `docs/eluon.json`을 자동으로 읽어 현재 자산 30개가 붙습니다. 설치할 것 없습니다.

---

## 이 저장소가 다른 점

보통의 UI 킷은 이미지와 피그마 파일을 줍니다. Eluon은 거기에 **에이전트가 판단에 쓸 수 있는 것**을 함께 줍니다.

```json
{
  "id": "btn-danger-md",
  "spec":   { "height": 48, "radius": "md", "paddingX": 20, "typography": "body2-bold" },
  "tokens": { "bg": "danger.default", "label": "text.inverse" },
  "usage":  "되돌릴 수 없는 액션. 삭제·탈퇴·영구 해제",
  "dont":   "확인 모달 없이 단독 노출 금지"
}
```

`spec`이 있으니 눈대중으로 재지 않고, `tokens`가 있으니 헥스를 하드코딩하지 않고,
`dont`가 있으니 잘못된 자리에 놓지 않습니다.

그리고 **이 spec은 문서가 아니라 소스입니다.** `recipes/components.py`의 spec 수치가
그대로 CSS가 되고 그대로 PNG로 렌더되기 때문에, 문서와 실물이 어긋날 수 없습니다.

---

## 테마

| 테마 | 브랜드 | 라운드 | 언제 |
|---|---|---|---|
| `core` | 중립 블루 | md 10 / lg 12 | 고객사 브랜드 미정, 구조만 보여줄 때 |
| `eluo` | Navy `#000080` | md 6 / lg 8 | 자사 제안·내부 산출물 기본값 |
| `atlas` | 딥 네이비 `#001F45` | md 4 / lg 8 | 고객사 건 (가명. 첫 고객사 테마) |
| `ember` | 딥그린 `#12503C` | 전부 2 / 카드 3 | 고객사 건 (가명. 이름과 색이 다릅니다) |
| `harbor` | 웜 토프 `#816C58` | 0 / 4 / 4 / 0 | 고객사 건 (가명. 웹사이트에서 추출) |
| `tideland` | 테라코타 `#B44E2B` | 8 / 14 / 20 / 28 | 고객사 건 (가명. **추정값 — 실측 아님**) |
| `cobalt` | 네이비 `#051469` | 전부 999(알약) / 카드 0 | 고객사 건 (가명. 웹사이트에서 추출) |

**고객사 테마 추가는 컴포넌트를 건드리지 않습니다.**
색·라운드뿐 아니라 **크기·패딩도 고객사 실측값**을 넣습니다 (`semantic.size`).

```bash
cp tokens/theme-eluo.json tokens/theme-<고객사>.json
# semantic.color 의 brand.* 만 교체
# eluon.config.json 의 themes 배열에 <고객사> 추가 — 안 하면 스크립트가 무시합니다
python3 scripts/build_tokens.py && python3 scripts/check_contrast.py
python3 scripts/render.py && python3 scripts/build_manifest.py && python3 scripts/build_pb_manifest.py \
  && python3 scripts/make_montage.py
```

`check_contrast.py`가 대비비 미달을 배포 전에 잡습니다. 브랜드색 위 흰 텍스트가 안 읽히는 사고가 가장 흔합니다.

---

## 컴포넌트 추가하기

이미지를 만들어 넣는 게 아니라 **레시피에 dict 하나를 더합니다.**

```python
# recipes/components.py
add(
    id="btn-tertiary-md", name="Tertiary Button / MD", group="button",
    tags=["보조", "낮은위계"],
    spec={"height": 48, "radius": "md", "paddingX": 16, "typography": "body2-bold"},
    tokens={"bg": "surface.subtle", "label": "text.primary"},
    usage="...", dont="...",
    css=f".c{{...}}", html='<button class="c">라벨</button>',
)
```

그리고 파이프라인을 돌립니다.

```bash
python3 scripts/build_tokens.py    # 토큰 → CSS 변수 (--size-* · --bp-* 포함)
python3 scripts/render.py          # 레시피 → @2x PNG (테마별) + 사이드카
python3 scripts/build_manifest.py  # 사이드카 → manifest.json + 목록
python3 scripts/build_pb_manifest.py  # → docs/eluon.json (프롬프트 빌더용)
python3 scripts/make_montage.py    # → 몽타주 시트
python3 scripts/build_docs.py      # → 문서 사이트
python3 scripts/check_contrast.py  # 대비비 검사
```

---

## 릴리즈

자산 URL은 릴리즈 태그에 고정됩니다.

```bash
# eluon.config.json 의 version 을 v1.11.1 으로 수정
python3 scripts/build_manifest.py && python3 scripts/build_pb_manifest.py
git commit -am "release: v1.11.1" && git tag v1.11.1 && git push --tags
```

`@main`을 쓰지 않는 이유: jsDelivr가 브랜치 URL을 길게 캐싱해서, 자산을 교체해도
며칠간 옛 이미지가 나옵니다.

---

## 폴더

```
CLAUDE.md                  에이전트 작업 계약서 (가장 중요)
eluon.config.json          org/repo/version/테마 설정
tokens/core.json           브랜드 중립 파운데이션      ← 사람이 고침
tokens/theme-eluo.json     ELUO 오버라이드            ← 사람이 고침
recipes/components.py      컴포넌트 정의               ← 사람이 고침
scripts/                   빌드 파이프라인 7종
─────────────────────────  아래는 전부 생성물. 직접 편집 금지
manifest.json              단일 진실 공급원
assets/components/         테마별 @2x PNG + 사이드카 JSON
index/ASSETS.md            사람이 읽는 목록
index/sheet-<theme>.png    몽타주 시트
docs/index.html            공개 문서 사이트 (GitHub Pages)
docs/eluon.json            프롬프트 빌더가 읽는 변환본
docs/prompt-builder.html   프롬프트 빌더 (생성물 아님. 손으로 고침)
```

---

## 이 저장소에 넣지 않는 것

- 고객사 로고, 실제 콘텐츠 이미지, 미공개 프로젝트 화면 → **private 저장소로 분리**
- 원본 `.fig` 파일 → 피그마에 두고 링크만
- 1회성 시안 → 라이브러리는 "두 번 이상 쓸 것"만

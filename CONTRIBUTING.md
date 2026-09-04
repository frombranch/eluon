# 기여 체크리스트

라이브러리가 망가지는 방식은 거의 항상 같습니다.
**비슷한 게 이미 있는데 하나 더 추가되는 것.** 그래서 1번이 가장 중요합니다.

---

## 컴포넌트 추가

### 추가 전
- [ ] **`index/ASSETS.md`에서 유사 자산을 먼저 찾았다.**
      비슷한 게 있으면 새로 만들지 말고 기존 자산에 `state`나 `variant`를 더할 수 있는지 검토
- [ ] 이 컴포넌트를 **앞으로 두 번 이상** 쓸 것이다 (1회성이면 프로젝트 저장소에 둡니다)
- [ ] `spec`으로 설명되는 차이인지, 정말 새 자산이어야 하는지 판단했다

### 레시피 작성 (`recipes/components.py`)
- [ ] ID가 [`NAMING.md`](./NAMING.md) 규칙과 일치
- [ ] `spec`에 **height / radius / paddingX / typography**가 들어 있다
- [ ] CSS에서 색을 `var(--color-*)` 시맨틱 토큰으로만 참조했다 (헥스 직접 사용 ✗)
- [ ] 라운드를 `var(--radius-*)`로 참조했다 (테마마다 값이 다름)
- [ ] `spec`의 수치가 CSS에 그대로 들어갔다 (f-string으로 흘려보냄)
- [ ] `usage` 한 문장, `dont` 한 문장을 채웠다
      → "언제 쓰나"보다 **"언제 쓰면 안 되나"**가 실제로는 더 자주 필요합니다
- [ ] 예시 텍스트가 실제로 쓸 법한 한국어다 (`Lorem ipsum`, `Button` ✗)

### 커밋 전
```bash
python3 scripts/build_tokens.py
python3 scripts/render.py
python3 scripts/build_manifest.py
python3 scripts/make_montage.py
python3 scripts/build_docs.py
python3 scripts/check_contrast.py
```
- [ ] 여섯 스크립트가 모두 성공
- [ ] 생성물(`manifest.json` `index/` `docs/` `assets/**/*.png`)을 함께 커밋
- [ ] 몽타주 시트에서 새 컴포넌트가 제대로 보이는지 눈으로 확인

---

## 테마 추가 (고객사)

```bash
cp tokens/theme-eluo.json tokens/theme-<고객사>.json
# semantic.color 의 brand.* 와 필요하면 radius 만 교체
# eluon.config.json 의 themes 배열에 추가
python3 scripts/build_tokens.py && python3 scripts/check_contrast.py
```

- [ ] **컴포넌트 레시피를 건드리지 않았다.** 건드렸다면 그건 테마가 아니라 새 컴포넌트입니다
- [ ] `check_contrast.py`가 전부 통과 — 브랜드색 위 흰 텍스트가 안 읽히는 사고가 가장 흔합니다
- [ ] `rules` 배열에 그 브랜드 특유의 주의사항을 적었다 (예: 형광색은 면적 강조에만)

---

## 자산을 없앨 때

지우지 않습니다. **`status`를 `deprecated`로 바꾸고 `replacedBy`를 채웁니다.**
파일을 지우면 이미 배포된 시안·제안서의 이미지가 깨집니다.
실제 삭제는 다음 메이저 버전에서 일괄로.

---

## 리뷰 기준

시각적 완성도보다 **아래 셋**을 봅니다.

1. `usage` / `dont`가 실제 판단에 쓸 수 있게 구체적인가 — "적절히 사용" 같은 말은 반려
2. `spec` 수치만 보고 코드로 재현이 되는가
3. 기존 자산과 역할이 겹치지 않는가

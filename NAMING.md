# 이름 규칙

자산 이름은 사람이 검색하기 위한 것이 아니라 **에이전트가 오해 없이 지목하기 위한 것**입니다.
그래서 짧고, 예외를 두지 않습니다.

## ID

```
<group>-<variant>-<size>[-<state>]
```

| 조각 | 값 | 예 |
|---|---|---|
| `group` | 계열 | `btn` `chip` `input` `select` `card` `tab` `table` `toast` `badge` `modal` `pagination` `price` `wish` `section` |
| `variant` | 성격 | `primary` `secondary` `ghost` `danger` `outline` `filter` `basic` `product` `underline` `discount` `toggle` `header` |
| `size` | 크기 | `sm` `md` `lg` |
| `state` | 상태(기본형은 생략) | `hover` `focus` `error` `disabled` `selected` |

예: `btn-primary-lg` · `btn-primary-lg-disabled` · `input-text-md-error` · `chip-filter-md-selected`

**금지:** 한글 ID, 공백, 대문자, ID에 버전 넣기(`btn-primary-lg-v2` ✗ — 버전은 릴리즈 태그로).

## 파일

렌더러가 자동으로 만듭니다. 손으로 이름 붙일 일이 없습니다.

```
assets/components/<group 풀네임>/<id>--<theme>@2x.png
assets/components/<group 풀네임>/<id>.json
```

| ID 접두 | 폴더 |
|---|---|
| `btn-` | `button/` |
| `chip-` | `chip/` |
| `input-` `select-` | `input/` |
| `card-` | `card/` |
| `tab-` `pagination-` | `navigation/` |
| `table-` | `table/` |
| `toast-` | `feedback/` |
| `badge-` | `badge/` |
| `modal-` | `modal/` |
| `price-` `wish-` | `commerce/` |
| `section-` | `layout/` |

## 상태(state) 자산은 언제 만드는가

전부 만들지 않습니다. **`spec`이나 `tokens`로 설명이 안 되는 것만** 별도 자산으로 만듭니다.

- 만든다 — 시각적으로 크게 다른 상태: `input-text-md-error`(테두리+헬퍼 텍스트), `chip-filter-md-selected`(배경 채움), `btn-primary-lg-disabled`
- 안 만든다 — 색만 한 단계 어두워지는 hover: `tokens`의 `brand.primary.hover`에 값으로 기록하고 끝냅니다

상태를 이미지로 다 찍으면 자산이 세 배로 늘고, 그중 대부분은 아무도 안 봅니다.

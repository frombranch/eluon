# 자산 목록

`frombranch/eluon` · **v1.11.1** · 총 36개(상태 변형 5개 별도) · 테마 eluo, atlas, ember, harbor, tideland, cobalt

> `scripts/build_manifest.py`가 생성합니다. 직접 고치지 마세요.
> 아래 규격은 **eluo** 테마 기준입니다. 치수는 테마마다 다릅니다 — `manifest.json`의 `specByTheme`를 보십시오.

## badge (1)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `badge-status-sm` | Status Badge / SM | h24 r:full | 행·카드의 상태 표기. 색과 텍스트를 함께 씀 | 색만으로 상태를 구분하지 않음 |

## button (8)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `btn-danger-md` | Danger Button / MD | h48 r:md | 되돌릴 수 없는 액션. 삭제·탈퇴·영구 해제 | 확인 모달 없이 단독 노출 금지 |
| `btn-ghost-md` | Ghost Button / MD | h48 r:md | 세 번째 순위 액션. 취소·더보기·되돌리기 | 한 화면에 3개 이상 늘어놓지 않음. 위계가 사라짐 |
| `btn-outline-lg` | Outline Button / LG | h56 r:lg | 채움형이 과한 화면의 주요 액션. 버튼이 화면에서 여러 번 반복될 때 | btn-primary와 같은 화면에 섞지 않음. 어느 쪽이 주요 액션인지 흐려짐 |
| `btn-outline-md` | Outline Button / MD | h48 r:md | 카드·행 안의 반복 액션. 장바구니 담기·상세 보기 | btn-primary와 같은 화면에 섞지 않음. 어느 쪽이 주요 액션인지 흐려짐 |
| `btn-primary-lg` | Primary Button / LG<br><small>상태 · `btn-primary-lg-disabled`</small> | h56 r:lg | 화면당 주요 액션 1개. 히어로·폼 제출·전환 유도 | 삭제·탈퇴 등 파괴적 액션에는 사용 금지 (btn-danger-md 사용) |
| `btn-primary-md` | Primary Button / MD | h48 r:md | 본문 안 액션. 카드 내부나 테이블 행 액션 | 삭제·탈퇴 등 파괴적 액션에는 사용 금지 (btn-danger-md 사용) |
| `btn-primary-sm` | Primary Button / SM | h36 r:sm | 밀도 높은 영역. 툴바·필터 바 | 삭제·탈퇴 등 파괴적 액션에는 사용 금지 (btn-danger-md 사용) |
| `btn-secondary-lg` | Secondary Button / LG | h56 r:lg | 주요 액션과 나란히 놓는 두 번째 선택지 | 단독으로 쓰지 않음. 항상 primary와 짝 |

## card (4)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `card-basic-md` | Basic Card / MD | w320 r:xl | 구획을 나누는 기본 컨테이너 | 카드 안에 또 카드를 넣지 않음 |
| `card-portrait-md` | Portrait Card / MD | w280 r:xl | 세로 이미지가 주인공인 목록. SNS·영상·인물 카드. 4~6열로 늘어놓을 때 | 가로 이미지를 억지로 넣지 않음. 16:9 면 card-product-md |
| `card-product-md` | Product Card / MD | w320 r:xl | 그리드형 목록의 기본 단위. 3~4열 그리드 | 썸네일 비율을 카드마다 다르게 두지 않음 |
| `card-stat-md` | Stat Card / MD | w320 r:xl | 숫자 하나를 앞세우는 지표 묶음. 혜택·실적을 3~4개 나란히 놓을 때 | 숫자가 없으면 쓰지 않음. 그냥 구획이면 card-basic-md |

## chip (1)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `chip-filter-md` | Filter Chip / MD<br><small>상태 · `chip-filter-md-selected`</small> | h36 r:full | 목록 상단의 다중 필터. 2~8개까지 | 단일 선택에는 쓰지 않음. 그건 탭이나 셀렉트 |

## commerce (2)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `price-discount-md` | Price / Discount / MD | — | 할인율·판매가·정가를 한 줄로. 목록과 상세에서 순서를 바꾸지 않음 | 정가에 취소선 없이 두 가격을 나란히 두지 않음. 어느 쪽이 낼 돈인지 알 수 없음 |
| `wish-toggle-md` | Wish Toggle / MD<br><small>상태 · `wish-toggle-md-selected`</small> | h40 w40 r:full | 목록 카드의 관심 등록. 40x40 터치 영역을 확보한 최소 크기 | 선택 상태를 색으로만 표시하지 않음. 하트를 채워 모양도 함께 바꿈 |

## disclosure (1)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `accordion-md` | Accordion / MD | — | 질문·항목이 길어 한 번에 다 보이면 부담스러운 목록. FAQ·약관·상세 사양 | 한 번에 다 읽어야 하는 내용을 접지 않음. 접힌 것은 안 읽습니다 |

## feedback (3)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `empty-state-md` | Empty State / MD | — | 목록이 비었을 때. 왜 비었는지와 다음에 무엇을 할지를 같이 적음 | '데이터가 없습니다'만 쓰지 않음. 왜 없는지·무엇을 하면 되는지가 빠지면 막힙니다 |
| `toast-error-md` | Toast / Error / MD | w360 r:xl | 실패 통보. 자동으로 사라지지 않고 사용자가 닫음 | 원인 설명 없이 '오류가 발생했습니다'만 쓰지 않음 |
| `toast-info-md` | Toast / Info / MD | w360 r:xl | 되돌릴 필요 없는 결과 통보. 4초 후 자동 사라짐 | 에러나 확인이 필요한 내용에 쓰지 않음. 사용자가 놓침 |

## input (2)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `input-text-md` | Text Field / MD<br><small>상태 · `input-text-md-error` · `input-text-md-focus`</small> | h52 w320 r:md | 한 줄 입력의 기본형 | 라벨 없이 placeholder만으로 쓰지 않음 |
| `select-md` | Select / MD | h52 w320 r:md | 선택지 6개 이상의 단일 선택 | 선택지 5개 이하면 탭이나 라디오가 더 빠름 |

## layout (9)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `cta-band-lg` | CTA Band / LG | w1200 r:xl | 섹션과 섹션 사이, 또는 페이지 끝의 전환 유도. 한 페이지에 하나 | 본문 정보를 여기 넣지 않음. 제목 한 줄·리드 한 줄·버튼 하나까지 |
| `desc-list-md` | Description List / MD | — | 라벨과 값이 짝인 목록. 회사 개요·사양·계약 조건 | 비교가 필요하면 목록이 아니라 표. table-basic-lg 로 |
| `footer-lg` | Footer / LG | w1200 | 모든 페이지 최하단. 로고 · 고지 · 보조 메뉴 | 색을 흐리게 해서 구분하지 않음. 뒤집힌 면에서는 대비가 무너짐. 크기와 굵기로 나눔 |
| `form-field-md` | Form Field / MD | w320 r:md | 라벨 · 입력 · 도움말을 한 묶음으로. 폼의 최소 단위 | 라벨을 placeholder 로 대신하지 않음. 입력하면 라벨이 사라짐 |
| `header-gnb-lg` | Header / GNB / LG | h72 w1200 | 모든 페이지 최상단. 로고 · 주 메뉴 · 주요 액션 하나 | 메뉴가 7개를 넘기면 여기 다 넣지 않음. 드롭다운이나 2단으로 나눔 |
| `hero-split-lg` | Hero / Split / LG | w1200 | 페이지 첫 화면. 제목·리드·액션을 왼쪽에, 핵심 수치 레일을 오른쪽에 | 한 화면에 두 번 쓰지 않음. 무엇이 이 페이지의 주제인지 흐려짐 |
| `list-row-md` | List Row / MD | — | 제목·메타·값이 한 줄인 목록. 공지·뉴스·자료실 | 열이 셋을 넘게 비교해야 하면 목록이 아니라 표. table-basic-lg 로 |
| `section-header-md` | Section Header / MD | — | 섹션 시작의 제목 묶음. 아이브로우(선택) · 제목 · 리드문을 한 덩어리로 | 리드문이 세 줄을 넘기면 리드가 아니라 본문. 본문은 섹션 안으로 내림 |
| `step-flow-md` | Step Flow / MD | — | 순서가 있는 절차. 신청 방법·심사 과정·이용 안내 | 순서가 없는 목록에 번호를 붙이지 않음. 번호는 순서가 있다는 약속입니다 |

## modal (1)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `modal-confirm-lg` | Confirm Modal / LG | w420 r:xl | 되돌릴 수 없는 액션 직전의 확인 | 단순 안내에 쓰지 않음. 그건 토스트 |

## navigation (3)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `breadcrumb-md` | Breadcrumb / MD | — | 세 단계 이상 깊은 페이지의 현재 위치. 목록 → 분류 → 상세 | 두 단계뿐인 구조에 쓰지 않음. 뒤로 가기 한 번이면 됩니다 |
| `pagination-md` | Pagination / MD | h40 r:md | 20개 이상 목록. 무한 스크롤이 부적절한 관리 화면 | 10페이지 이상 번호를 다 노출하지 않음. 축약 표기 사용 |
| `tab-underline-md` | Tab / Underline / MD | h52 w360 | 같은 층위의 목록을 전환. 2~5개 | 6개 이상이면 탭 대신 드롭다운 필터 |

## table (1)

| ID | 이름 | 규격 | 언제 쓰나 | 쓰면 안 되는 때 |
|---|---|---|---|---|
| `table-basic-lg` | Table / Basic / LG | w520 r:xl | 비교가 필요한 목록. 열이 3개 이상일 때 | 모바일에서 그대로 쓰지 않음. 카드로 전환 |

---
name: implement-auto-api
description: >
  Sinh code Playwright Python cho API test từ MEMORY.md + test_scenario_map.md
  (output của skill parse-tc-excel). Output gồm: conftest.py (fixtures, base config),
  test_[group].py (test functions theo nhóm), pages/api_client.py (helper gọi API).
  Trigger khi user nhắc đến: "gen code playwright", "sinh playwright python",
  "viết test automation", "implement auto từ TC", "gen test script",
  "tạo file test.py", "code playwright cho API", hoặc sau khi đã chạy parse-tc-excel
  và muốn tiếp tục sinh code. BẮT BUỘC có MEMORY.md trước — nếu chưa có,
  yêu cầu user chạy parse-tc-excel trước.
---

# Implement Auto API — Playwright Python

Sinh code Playwright Python từ MEMORY.md đã được tạo bởi `parse-tc-excel`.

---

## Vị trí trong Pipeline

```
parse-tc-excel
  (MEMORY.md + test_scenario_map.md)
        │
        ▼
★ implement-auto-api ★
        │
        ▼
tests/
  conftest.py
  test_auth.py
  test_validate.py
  test_business_rule.py
  test_happy_path.py
  test_state_transition.py
  test_idempotency.py
  test_error_handling.py
  test_data_consistency.py
pages/
  api_client.py
config/
  settings.py
```

---

## Cấu trúc project output chuẩn

```
playwright-api-tests/
├── config/
│   └── settings.py          # BASE_URL, timeout, env config
├── pages/
│   └── api_client.py        # APIClient wrapper — gọi request, handle auth
├── tests/
│   ├── conftest.py          # Fixtures: client, tokens, bundle data
│   ├── test_auth.py
│   ├── test_validate_required.py
│   ├── test_validate_format.py
│   ├── test_business_rule.py
│   ├── test_happy_path.py
│   ├── test_state_transition.py
│   ├── test_idempotency.py
│   ├── test_error_handling.py
│   └── test_data_consistency.py
├── pytest.ini               # pytest config
└── requirements.txt         # playwright, pytest, pytest-playwright
```

---

## Workflow

### Step 0: Kiểm tra prerequisite

Kiểm tra MEMORY.md có tồn tại không:
```
Nếu không tìm thấy MEMORY.md:
→ "Chưa có MEMORY.md. Vợ chạy skill parse-tc-excel trước nhé để parse file TC Excel."
→ DỪNG
```

Đọc các file:
1. `MEMORY.md` — lấy: Base URL, API endpoint, auth scheme, TC summary
2. `test_scenario_map.md` — lấy: từng TC detail theo cấu trúc mới:
   - `Pre-condition` → token dùng, data object, DB state cần trước khi test
   - `Steps` → method, url, headers, body/params (từng bước đánh số)
   - `Expected Status` + `Response Assertions` + `DB Assertions` → assertions
   - `Blocked Note` → comment PARTIAL
3. `test_data_catalog.md` — lấy: danh sách data objects
4. `api_schema.md` — lấy: request/response schema

---

### Step 1: Sinh config/settings.py

```python
# config/settings.py

BASE_URL = "https://staging.tongdaiwifi.vn"
API_VERSION = "v1"
TIMEOUT = 30_000  # ms

# Endpoints
ENDPOINT_BUNDLE_DETAIL = "/v1/bundles/{bundle_id}"

# Default params
DEFAULT_CHANNEL = "FPT_WEB"
DEFAULT_CUSTOMER_TYPE = "KH_MOI"
```

---

### Step 2: Sinh pages/api_client.py

Wrapper cho Playwright `APIRequestContext`:

```python
# pages/api_client.py

from playwright.sync_api import APIRequestContext
from config.settings import BASE_URL, TIMEOUT


class APIClient:
    def __init__(self, request: APIRequestContext, token: str = None):
        self.request = request
        self.token = token

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_bundle_detail(
        self,
        bundle_id: str,
        channel_code: str = "FPT_WEB",
        customer_type: str = "KH_MOI",
        location: dict = None,
        cycle: list = None,
    ):
        """GET /v1/bundles/{bundleId}"""
        params = {
            "channelCode": channel_code,
            "customerType": customer_type,
        }
        if location:
            params.update({
                "location.ward": location.get("ward"),
                "location.district": location.get("district"),
                "location.city": location.get("city"),
            })
            # Xóa key None
            params = {k: v for k, v in params.items() if v is not None}
        if cycle:
            params["cycle"] = cycle

        return self.request.get(
            f"{BASE_URL}/v1/bundles/{bundle_id}",
            headers=self._headers(),
            params=params,
            timeout=TIMEOUT,
        )
```

---

### Step 3: Sinh tests/conftest.py

```python
# tests/conftest.py

import pytest
from playwright.sync_api import Playwright
from pages.api_client import APIClient


# ─── Tokens ────────────────────────────────────────────────────────────
# TODO: Điền giá trị thực từ môi trường staging trước khi chạy
TOKENS = {
    "TOKEN_VALID":    "REPLACE_WITH_REAL_TOKEN",
    "TOKEN_EXPIRED":  "REPLACE_WITH_EXPIRED_TOKEN",
    "TOKEN_INVALID":  "INVALID_XYZ123_FAKE_TOKEN",
    "TOKEN_NO_PERM":  "REPLACE_WITH_LOW_ROLE_TOKEN",
}

# ─── Bundle IDs ─────────────────────────────────────────────────────────
# TODO: Điền bundleId thực từ DB staging
BUNDLE_IDS = {
    "BUNDLE_VALID_001":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_VALID_002":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_VALID_003":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_VALID_004":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_VALID_005":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_NOT_EXIST_001":         "NON_EXISTENT_BUNDLE_XYZ_999",
    "BUNDLE_INACTIVE_001":          "REPLACE_WITH_INACTIVE_BUNDLE_ID",
    "BUNDLE_NO_VALID_PRICE_001":    "REPLACE_WITH_BUNDLE_NO_VALID_PRICE",
    "BUNDLE_WITH_DEVICE_001":       "REPLACE_WITH_BUNDLE_WITH_PHYSICAL_SKU",
    "BUNDLE_NO_DEVICE_001":         "REPLACE_WITH_BUNDLE_ALL_DIGITAL",
    "BUNDLE_CYCLE_001":             "REPLACE_WITH_BUNDLE_MULTI_CYCLE",
    "BUNDLE_OTP_001":               "REPLACE_WITH_BUNDLE_ONE_TIME_PAYMENT",
    "BUNDLE_MULTI_PRICE_001":       "REPLACE_WITH_BUNDLE_MULTI_PRICE",
    "BUNDLE_LOCATION_001":          "REPLACE_WITH_BUNDLE_SINGLE_LOCATION_PRICE",
    "BUNDLE_MULTI_LOCATION_001":    "REPLACE_WITH_BUNDLE_MULTI_LOCATION_PRICE",
    "BUNDLE_APP_ONLY_001":          "REPLACE_WITH_BUNDLE_APP_CHANNEL_ONLY",
    "BUNDLE_CROSSSELL_001":         "REPLACE_WITH_BUNDLE_CROSSSELL_ALLOWED",
    "BUNDLE_NO_CROSSSELL_001":      "REPLACE_WITH_BUNDLE_CROSSSELL_NOT_ALLOWED",
    "BUNDLE_FULL_001":              "REPLACE_WITH_BUNDLE_FULL_DATA",
    "BUNDLE_E2E_001":               "REPLACE_WITH_BUNDLE_E2E_TRUE",
    "BUNDLE_NON_E2E_001":           "REPLACE_WITH_BUNDLE_E2E_FALSE",
    "BUNDLE_PAYMENT_001":           "REPLACE_WITH_BUNDLE_MULTI_PAYMENT_METHOD",
    "BUNDLE_PRICE_001":             "REPLACE_WITH_BUNDLE_PRICE_ALL_TYPES",
    "BUNDLE_SKU_001":               "REPLACE_WITH_BUNDLE_MIXED_SKU",
    "BUNDLE_BONUS_001":             "REPLACE_WITH_BUNDLE_BONUS_MONTH",
    "BUNDLE_TIER_001":              "REPLACE_WITH_BUNDLE_TIER_PRICE",
    "BUNDLE_FEE_001":               "REPLACE_WITH_BUNDLE_WITH_ATTACHMENT_FEE",
    "BUNDLE_MULTI_CYCLE_001":       "REPLACE_WITH_BUNDLE_FEE_MULTI_CYCLE",
    "BUNDLE_GROUP_SKU_001":         "REPLACE_WITH_BUNDLE_SKU_GROUP",
    "BUNDLE_DEPENDENCY_001":        "REPLACE_WITH_BUNDLE_WITH_DEPENDENCY_RULE",
    "BUNDLE_STATE_001":             "REPLACE_WITH_BUNDLE_FOR_STATE_TEST",
    "BUNDLE_IDEM_001":              "REPLACE_WITH_BUNDLE_FOR_IDEMPOTENCY",
    "BUNDLE_NO_CONTENT_001":        "REPLACE_WITH_BUNDLE_NO_CONTENT_CONFIG",
    "BUNDLE_WITH_CONTENT_001":      "REPLACE_WITH_BUNDLE_WITH_CONTENT_CONFIG",
    "BUNDLE_CONSISTENCY_001":       "REPLACE_WITH_BUNDLE_FOR_CONSISTENCY_TEST",
    "BUNDLE_CACHE_001":             "REPLACE_WITH_BUNDLE_FOR_CACHE_TEST",
    "BUNDLE_PERF_001":              "REPLACE_WITH_BUNDLE_FOR_PERF_TEST",
    "BUNDLE_NET_001":               "REPLACE_WITH_BUNDLE_FOR_NETWORK_TEST",
}


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright):
    context = playwright.request.new_context(base_url="https://staging.tongdaiwifi.vn")
    yield context
    context.dispose()


@pytest.fixture
def client(api_request_context):
    """APIClient không có token (dùng cho test không auth)"""
    return APIClient(api_request_context)


@pytest.fixture
def authed_client(api_request_context):
    """APIClient với token hợp lệ"""
    return APIClient(api_request_context, token=TOKENS["TOKEN_VALID"])


def bundle(name: str) -> str:
    """Helper lấy bundleId từ catalog"""
    return BUNDLE_IDS[name]


def token(name: str) -> str:
    """Helper lấy token từ catalog"""
    return TOKENS[name]
```

---

### Step 4: Sinh test files theo group

#### Quy tắc đặt tên function:

```python
def test_TC_GBD_1_happy_path_auth():
    ...
```
- Prefix: `test_`
- TC ID: dấu `.` thay bằng `_`
- Tên ngắn từ title (snake_case, tối đa 5 từ)

#### Quy tắc comment cho PARTIAL và BLOCKED:

```python
# ⚠️ PARTIAL — TC_GBD.12
# BLOCKED: Spec chưa rõ khi thiếu district/city: trả 400 hay 200 không filter location?
# Assumption hiện tại: 400. Cập nhật expected_status khi BA/DEV confirm.
def test_TC_GBD_12_location_missing_district_city(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_004"),
        location={"ward": "Dịch Vọng Hậu"},  # thiếu district, city
    )
    # ASSUMPTION: expect 400 — update nếu BA confirm behavior khác
    assert response.status == 400
```

#### Mapping từ test_scenario_map.md → code:

```
Pre-condition section:
  Token: TOKEN_VALID          → fixture authed_client (dùng TOKEN_VALID)
  Token: TOKEN_EXPIRED        → APIClient(ctx, token=token("TOKEN_EXPIRED"))
  Data: BUNDLE_VALID_001      → bundle("BUNDLE_VALID_001")
  DB: ...                     → comment "# Pre-condition: ..." trong code

Steps section (bước 1 — Gọi API):
  Method: GET                 → authed_client.get_bundle_detail(...)
  URL: /v1/bundles/...        → bundle_id param
  Headers: Bearer TOKEN_VALID → đã handle qua fixture
  Params: { channelCode: ... }→ channel_code, customer_type params

Expected Status + Assertions:
  HTTP Status: 200            → assert response.status == 200
  response.data.X == Y        → assert data["data"]["X"] == "Y"
  DB: ...                     → comment "# DB: verify manually"
```

#### Pattern chuẩn cho mỗi TC:

```python
def test_TC_GBD_N_[tên_ngắn](authed_client):
    # Pre-condition: BUNDLE_VALID_001 (status=ACTIVE, có ≥1 dòng giá active)
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_XXX"),
        channel_code="FPT_WEB",
        customer_type="KH_MOI",
    )
    data = response.json()

    # Assert HTTP status
    assert response.status == 200

    # Assert response fields
    assert data["data"]["bundleId"] == bundle("BUNDLE_XXX")
    assert data["data"]["status"] == "ACTIVE"
    assert len(data["data"]["PriceListBundle"]) >= 1
```

---

### Step 4a: tests/test_auth.py

```python
# tests/test_auth.py
# Group: Authentication & Authorization
# TC: TC_GBD.1 → TC_GBD.5

import pytest
from tests.conftest import bundle, token
from pages.api_client import APIClient


# ─── TC_GBD.1 ────────────────────────────────────────────────────────────
def test_TC_GBD_1_happy_path_valid_token(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["bundleId"] == bundle("BUNDLE_VALID_001")
    assert data["data"]["status"] == "ACTIVE"
    assert len(data["data"]["PriceListBundle"]) >= 1


# ─── TC_GBD.2 ────────────────────────────────────────────────────────────
def test_TC_GBD_2_no_authorization_header(api_request_context):
    client_no_token = APIClient(api_request_context, token=None)
    response = client_no_token.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401
    data = response.json()
    assert "data" not in data or data.get("data") is None


# ─── TC_GBD.3 ────────────────────────────────────────────────────────────
def test_TC_GBD_3_invalid_token(api_request_context):
    client_invalid = APIClient(api_request_context, token=token("TOKEN_INVALID"))
    response = client_invalid.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401


# ─── TC_GBD.4 ────────────────────────────────────────────────────────────
def test_TC_GBD_4_expired_token(api_request_context):
    client_expired = APIClient(api_request_context, token=token("TOKEN_EXPIRED"))
    response = client_expired.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401


# ─── TC_GBD.5 ────────────────────────────────────────────────────────────
def test_TC_GBD_5_token_no_permission(api_request_context):
    client_no_perm = APIClient(api_request_context, token=token("TOKEN_NO_PERM"))
    response = client_no_perm.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 403
```

---

### Step 4b — 4h: Các file test còn lại

Sinh theo cùng pattern. Xem quy tắc đặc biệt theo group:

#### test_validate_required.py (TC_GBD.6 → 11)
- TC_GBD.6: path `/v1/bundles/` (không có bundleId) → assert 400 hoặc 404
- TC_GBD.7: bundleId = BUNDLE_NOT_EXIST_001 → assert 404
- TC_GBD.8: không truyền channelCode → assert 400
- TC_GBD.9: channelCode=INVALID_CHANNEL → assert 400
- TC_GBD.10: không truyền customerType → assert 400
- TC_GBD.11: customerType=INVALID_TYPE → assert 400

#### test_validate_format.py (TC_GBD.12 → 18)
- TC_GBD.12, 14: PARTIAL — comment BLOCKED
- TC_GBD.13: location thiếu city → assert 400
- TC_GBD.15: cycle=abc → assert 400
- TC_GBD.16: cycle=[3,6] OR condition → assert chỉ trả dòng giá cycle 3 và 6
- TC_GBD.17: không truyền cycle → assert trả toàn bộ
- TC_GBD.18: cycle truyền vào bundle OTP → assert bỏ qua cycle, trả 200

#### test_business_rule.py (TC_GBD.19 → 31)
- BR01: TC_GBD.19 (no valid price → 404/empty), TC_GBD.20 (PARTIAL-BLOCKED)
- BR02: TC_GBD.21 (min price toàn quốc), TC_GBD.22 (đúng 1 giá khu vực), TC_GBD.23 (min khu vực)
- BR03: TC_GBD.24 (deploy.isRequired=true), TC_GBD.25 (deploy.isRequired=false)
- BR04: TC_GBD.26 (PARTIAL), TC_GBD.27 (PARTIAL)
- BR05: TC_GBD.28 (channel scoping 404), TC_GBD.29 (channel scoping 200)
- BR06: TC_GBD.30 (crosssell=1), TC_GBD.31 (crosssell=0)

#### test_happy_path.py (TC_GBD.32 → 42)
- TC_GBD.32: full fields không null
- TC_GBD.33: isEndToEndSelling true/false
- TC_GBD.34: paymentMethods (PARTIAL)
- TC_GBD.35: pricesummarylist structure
- TC_GBD.36: SKUList fields
- TC_GBD.37: advancedPricing BONUS_MONTH
- TC_GBD.38: advancedPricing TIER_PRICE
- TC_GBD.39: AttachmentFee structure
- TC_GBD.40: Ps_id per cycle (PARTIAL)
- TC_GBD.41: SKUGroupList IsOne=true
- TC_GBD.42: BundleDependencyRule

#### test_state_transition.py (TC_GBD.43)
- TC_GBD.43: PARTIAL — cần admin action ở giữa test

#### test_idempotency.py (TC_GBD.44)
```python
def test_TC_GBD_44_idempotent_get(authed_client):
    resp1 = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_IDEM_001"))
    resp2 = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_IDEM_001"))

    assert resp1.status == 200
    assert resp2.status == 200
    assert resp1.json()["data"] == resp2.json()["data"]
```

#### test_error_handling.py (TC_GBD.45 → 49)
- TC_GBD.45: SQL injection attempt → 400/404, không có 500
- TC_GBD.46: space URL-encoded → 400/404
- TC_GBD.47: Content-Type header = application/json
- TC_GBD.48: error response không lộ stack trace
- TC_GBD.49: POST method → 405

#### test_data_consistency.py (TC_GBD.52 → 54)
- TC_GBD.52, 53: assert API vs DB — cần DB fixture riêng
- TC_GBD.54: PARTIAL (cache)

**TC bị SKIP (không gen file):** TC_GBD.50, 51 (performance cần JMeter/k6), TC_GBD.55, 56 (network cần Charles Proxy)

---

### Step 5: Sinh pytest.ini

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short
markers =
    full: TC auto hoàn toàn
    partial: TC auto một phần (có BLOCKED assumptions)
    skip_auto: TC không auto được (performance, network)
```

---

### Step 6: Sinh requirements.txt

```
playwright>=1.44.0
pytest>=8.0.0
pytest-playwright>=0.5.0
python-dotenv>=1.0.0
```

---

### Step 7: Present output

Sau khi sinh xong tất cả file, present toàn bộ và in tóm tắt:

```
✅ Sinh code Playwright Python hoàn tất!

📁 Cấu trúc project:
playwright-api-tests/
├── config/settings.py
├── pages/api_client.py
├── tests/
│   ├── conftest.py         ← QUAN TRỌNG: điền token + bundleId thực vào đây
│   ├── test_auth.py        (5 TC)
│   ├── test_validate_required.py  (6 TC)
│   ├── test_validate_format.py    (7 TC)
│   ├── test_business_rule.py      (13 TC)
│   ├── test_happy_path.py         (11 TC)
│   ├── test_state_transition.py   (1 TC — PARTIAL)
│   ├── test_idempotency.py        (1 TC)
│   ├── test_error_handling.py     (5 TC)
│   └── test_data_consistency.py   (3 TC)
├── pytest.ini
└── requirements.txt

📊 Tổng kết:
- FULL (chạy thẳng): N TC
- PARTIAL (có comment BLOCKED): N TC  ← cần confirm BA/DEV rồi update expected
- SKIP (không gen): N TC  ← TC_GBD.50, 51, 55, 56

⚙️ Bước tiếp theo:
1. pip install -r requirements.txt
2. playwright install
3. Điền giá trị thực vào conftest.py (TOKENS + BUNDLE_IDS)
4. pytest tests/ -v
```

---

## Quy tắc code quan trọng

### Q1 — Mỗi TC là 1 function độc lập
Không share state giữa các test. Mỗi function tự setup đủ data.

### Q2 — PARTIAL comment bắt buộc 3 dòng
```python
# ⚠️ PARTIAL — TC_GBD.XX
# BLOCKED: [copy nguyên văn Blocked Note từ test_scenario_map.md]
# Assumption: [giải thích assumption đang dùng] — cập nhật khi confirm.
# Pre-condition: [copy từ Pre-condition section nếu có DB state đặc biệt]
```

Ví dụ sinh từ TC có Pre-condition + Steps tách biệt:
```python
# ⚠️ PARTIAL — TC_GBD.12
# BLOCKED: Spec chưa rõ khi location.ward có nhưng thiếu district/city: trả 400 hay 200?
# Assumption: expect 400 — cập nhật khi BA/DEV confirm.
def test_TC_GBD_12_location_missing_district_city(authed_client):
    # Pre-condition: BUNDLE_VALID_004, TOKEN_VALID
    # Steps: GET /v1/bundles/{BUNDLE_VALID_004}, chỉ truyền location.ward
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_004"),
        location={"ward": "Dịch Vọng Hậu"},  # thiếu district, city
    )
    # ASSUMPTION: expect 400 — update nếu BA confirm behavior khác
    assert response.status == 400
```

### Q3 — Assert theo độ ưu tiên
1. HTTP status — assert trước tiên
2. Response fields — assert từng field cụ thể
3. DB assertions — comment `# DB: verify manually` nếu không có DB fixture

### Q4 — Không hardcode bundleId hay token trong test function
Luôn dùng helper `bundle("NAME")` và `token("NAME")` từ conftest.

### Q5 — URL path phải dùng từ settings
```python
# ❌ Sai
response = client.request.get("https://staging.tongdaiwifi.vn/v1/bundles/123")

# ✅ Đúng
response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))
```

### Q6 — SKIP TC: không gen file, chỉ ghi note
Trong README hoặc comment đầu file test nhắc:
```python
# TC_GBD.50, 51 — Performance: dùng JMeter/k6, không gen Playwright
# TC_GBD.55, 56 — Network timeout: cần Charles Proxy, không gen Playwright
```

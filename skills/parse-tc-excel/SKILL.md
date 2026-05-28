---
name: parse-tc-excel
description: >
  Đọc file Test Case (.xlsx) và file API Spec (.xlsx) của dự án ECOM/FPT Telecom,
  chuẩn hóa thành MEMORY.md + test_scenario_map.md để skill implement-auto-api
  sinh code Playwright Python. Trigger khi user nhắc đến: "parse TC excel",
  "đọc file testcase", "chuẩn bị auto từ Excel", "convert TC sang auto",
  "đọc file TC để gen playwright", "parse spec api", hoặc cung cấp 2 file xlsx
  (TC + API spec) và yêu cầu chạy automation. Skill này là bước bắt buộc TRƯỚC
  khi gọi implement-auto-api — không có MEMORY.md thì không gen code được.
---

# Parse TC Excel → MEMORY.md

Đọc 2 file Excel đầu vào, chuẩn hóa thành các file Markdown làm input cho
skill `implement-auto-api` sinh Playwright Python.

---

## Vị trí trong Pipeline

```
[TC Excel + API Spec Excel]
        │
        ▼
★ parse-tc-excel ★  →  implement-auto-api  →  tests/*.py
   (MEMORY.md)            (conftest.py)
```

| Hướng | Nguồn | Nội dung |
|-------|-------|----------|
| Input | File TC `.xlsx` | TC ID, Priority, Test Title, Request Body / Query Params, Expected Result, Khả Năng Auto |
| Input | File API Spec `.xlsx` | Endpoint, Method, Input fields, Required, Data type, Output schema, Business Rules |
| Output | `MEMORY.md` | Tổng hợp context cho implement-auto-api |
| Output | `test_scenario_map.md` | Chi tiết từng TC đã parse, kèm auto-tag |
| Output | `test_data_catalog.md` | Tất cả data object dùng trong TC (TOKEN_*, BUNDLE_*) |
| Output | `api_schema.md` | Request/response schema trích từ API spec |

---

## Cấu trúc file TC đầu vào (đã biết)

### File Test Case — cột chuẩn dự án:

| Cột | Tên | Ghi chú |
|-----|-----|---------|
| A | QC/AI | `AI` hoặc `QC` — bỏ qua khi parse |
| B | Testcase ID | `TC_GBD.1`, `TC_GBD.2`... — dùng làm ID |
| C | Priority | `High`, `Medium`, `Low` |
| D | Nội Dung Test (Test Title) | Tên TC — dùng làm test function name |
| E | Pre-condition / Test Data | Token dùng, data object, trạng thái DB cần có trước khi test |
| F | Các Bước Thực Hiện | Các bước: Method, URL, Headers, Body hoặc Params với giá trị cụ thể |
| G | Kết Quả Mong Đợi | Expected: HTTP status, response fields, DB |
| H | Khả Năng Auto | `✅ Auto được` / `⚠️ Auto được một phần` / `❌ Khó auto` |

**Row đặc biệt:**
- Row chỉ có 1 cell text (không có TC ID) → là **group header** — ghi nhận nhóm TC
- Row có TC ID nhưng cột B trống → sub-header của group — ghi nhận sub-group

### File API Spec — cấu trúc đã biết (Google Sheet dự án ECOM):

Sheet chứa API spec có structure:
- Header block: Method (GET/POST), Endpoint URL, Input type
- Input section: Field cấp 1→7, Required (M/O/Y), Data type, Ví dụ, Support (One/Many), Mô tả, Note
- Output section: tương tự Input
- Ví dụ API: JSON example thực tế

---

## Workflow

### Step 1: Nhận đầu vào

Xác định file đầu vào. Chấp nhận:
- Upload trực tiếp trong chat (path `/mnt/user-data/uploads/`)
- Link Google Sheet (dùng `google_drive_fetch`)
- Cả hai

Hỏi user nếu thiếu:
- "Vợ upload file TC và file API spec nhé, hoặc gửi link Google Sheet."

Xác nhận với user trước khi parse:
```
📂 Tìm thấy:
- File TC: [tên file] — [N] rows
- File API Spec: [tên file] / [sheet name]
- API: [METHOD] [endpoint URL]

Parse tất cả TC hay chỉ nhóm cụ thể?
```

---

### Step 2: Đọc file TC Excel

```
1. Đọc /mnt/skills/public/xlsx/SKILL.md để biết cách đọc Excel
2. Đọc file TC bằng Python openpyxl/pandas
3. Parse từng row:
   - Row có TC ID hợp lệ → TC object
   - Row không có TC ID → group header → ghi nhận current_group
4. Với mỗi TC, extract:
   - tc_id: cột B (ví dụ: TC_GBD.1)
   - priority: cột C
   - title: cột D
   - precondition: cột E — parse ra: token, data objects, DB state
   - steps: cột F — parse ra: method, url, headers, params/body
   - expected: cột G — parse ra: http_status, response_assertions[], db_assertions[]
   - auto_tag: cột H → map sang: FULL / PARTIAL / SKIP
   - group: group_header hiện tại
```

**Parse Pre-condition / Test Data (cột E):**
```python
# Từ cột E, extract:
# - "Token: TOKEN_*" → token_ref = "TOKEN_*"
# - "Data: BUNDLE_*" → data_objects = ["BUNDLE_*", ...]
# - "DB: ..." → db_preconditions = [...]
# Tất cả data object name (TOKEN_*, BUNDLE_*, ...) → thêm vào catalog
```

**Parse Các Bước Thực Hiện (cột F):**
```python
# Từ cột F, extract:
# - "Method: GET" → method = "GET"
# - "URL: /api/v1/..." → url_template = "/api/v1/..."
# - "Headers: {...}" → headers dict (bao gồm auth token)
# - "Body: {...}" → request_body dict (POST/PUT/PATCH)
# - "Params: {...}" → query_params dict (GET/DELETE)
# Data objects (TOKEN_*, BUNDLE_*...) extract từ giá trị của headers/body/params
```

**Parse Expected (cột G):**
```python
# Từ cột G, extract:
# - "HTTP Status: 200" → expected_status = 200
# - "response.data.X = Y" → response_assertions = [{"path": "data.X", "value": "Y"}]
# - "DB: ..." → db_assertions = [...]
# - "[BLOCKED...]" → blocked_note = "..."
```

**Map auto_tag:**
```python
AUTO_TAG_MAP = {
    "✅ Auto được": "FULL",
    "⚠️ Auto được một phần": "PARTIAL",
    "❌ Khó auto": "SKIP",
}
```

---

### Step 3: Đọc file API Spec

```
1. Đọc sheet chứa spec API (ưu tiên sheet được chỉ định)
2. Extract:
   - method: "GET" / "POST" / ...
   - base_path: "/v1/bundles/{bundleId}"
   - input_fields: list of {name, hierarchy, required, data_type, example, cardinality, description}
   - output_fields: list of {name, hierarchy, data_type, description}
   - business_rules: list of text từ cột Note/Mô tả có logic nghiệp vụ
   - json_example: JSON block ở cuối sheet (dùng làm response fixture)
3. Build URL template từ path + required params
4. Identify required fields (Required = M hoặc Y)
5. Identify optional fields (Required = O)
```

**Parse hierarchy (Field cấp 1 → 7):**
Các cột field có dạng nested — build json path:
```
Field cấp 1: "location"
Field cấp 2: "ward"
→ json_path = "location.ward"
```

---

### Step 4: Tạo file MEMORY.md

Lưu tại output directory (hoặc `/home/claude/` nếu không có project folder).

```markdown
# MEMORY — Parse TC Excel Output

> Tạo bởi skill parse-tc-excel
> Cập nhật lần cuối: [date]
> Dùng bởi: implement-auto-api

## 1. Project Info
- **Dự án:** ECOM Platform — Bundle API
- **Environment:** Staging
- **Base URL:** https://staging.tongdaiwifi.vn
- **API:** GET /v1/bundles/{bundleId}
- **Auth:** Bearer Token (header Authorization)

## 2. API Schema
- **File spec:** [tên file / link sheet]
- **Method:** GET
- **Endpoint:** /v1/bundles/{bundleId}
- **Required params:** bundleId (path), channelCode (query), customerType (query)
- **Optional params:** location.ward, location.district, location.city, cycle[], customerType
- **Response root:** { code, message, data: BundleDetail }

> Chi tiết schema → xem `api_schema.md`

## 3. TC Summary
| Group | Tổng TC | FULL | PARTIAL | SKIP |
|-------|---------|------|---------|------|
| Authentication & Authorization | N | n | n | n |
| Validate — Required Fields | N | n | n | n |
| Validate — Format / Type | N | n | n | n |
| Business Rule | N | n | n | n |
| Happy Path & Data Integrity | N | n | n | n |
| State Transition | N | n | n | n |
| Idempotency | N | n | n | n |
| Error Handling | N | n | n | n |
| Performance / Rate Limit | N | n | n | n |
| Data Consistency | N | n | n | n |
| Network / Timeout | N | n | n | n |
| **TỔNG** | **N** | **n** | **n** | **n** |

## 4. TC Index
| TC ID | Title ngắn | Group | Priority | Auto Tag | Blocked? |
|-------|-----------|-------|----------|----------|----------|
| TC_GBD.1 | Happy path auth | Authentication | High | FULL | — |
| TC_GBD.12 | Location thiếu district/city | Validate | Medium | PARTIAL | BLOCKED: trả 400 hay 200? |
| TC_GBD.50 | Response time performance | Performance | Low | SKIP | BLOCKED: SLA threshold? |
...

## 5. Data Objects Catalog
| Object | Dùng trong TC | Mô tả |
|--------|--------------|-------|
| TOKEN_VALID | TC_GBD.1, TC_GBD.6... | Bearer token hợp lệ, còn hạn |
| TOKEN_EXPIRED | TC_GBD.4 | Token đã hết hạn |
| TOKEN_INVALID | TC_GBD.3 | Token giả mạo |
| TOKEN_NO_PERM | TC_GBD.5 | Token hợp lệ, không đủ quyền |
| BUNDLE_VALID_001 | TC_GBD.1, TC_GBD.2... | Bundle active, có dòng giá hợp lệ |
...

> Chi tiết → xem `test_data_catalog.md`

## 6. BLOCKED / Cần confirm
| TC ID | Vấn đề | Ảnh hưởng |
|-------|--------|-----------|
| TC_GBD.12 | Location thiếu 1 phần: trả 400 hay 200 không filter? | PARTIAL — gen assert 400, comment note |
| TC_GBD.20 | Bundle INACTIVE: trả 404 hay 200 data rỗng? | PARTIAL |
| TC_GBD.50 | SLA response time chính thức? | SKIP |
| TC_GBD.51 | SLA concurrent 95th percentile? | SKIP |
| TC_GBD.55 | Network drop: tool simulate nào? | SKIP |
| TC_GBD.56 | Server timeout threshold? | SKIP |

## 7. File Reference
| File | Mô tả |
|------|-------|
| `MEMORY.md` | File này — index tổng quan |
| `test_scenario_map.md` | Chi tiết từng TC đã parse |
| `test_data_catalog.md` | Tất cả data objects |
| `api_schema.md` | Request/response schema đầy đủ |
```

---

### Step 5: Tạo file test_scenario_map.md

Mỗi TC là 1 entry chi tiết:

```markdown
# Test Scenario Map

## TC_GBD.1 — Happy path auth
- **Group:** Authentication & Authorization
- **Priority:** High
- **Auto Tag:** FULL
- **Pre-condition:**
  - Token: TOKEN_VALID (Bearer token hợp lệ, còn hạn)
  - Data: BUNDLE_VALID_001 (status=ACTIVE, có ≥1 dòng giá active+approved)
- **Steps:**
  1. Gọi API:
     Method: GET
     URL: /v1/bundles/BUNDLE_VALID_001
     Headers: { "Authorization": "Bearer TOKEN_VALID" }
     Params: { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
  2. Quan sát response trả về
- **Expected Status:** 200
- **Response Assertions:**
  - `data.bundleId` == "BUNDLE_VALID_001"
  - `data.status` == "ACTIVE"
  - `data.PriceListBundle` length >= 1
- **DB Assertions:** —
- **Blocked Note:** —

---

## TC_GBD.12 — Location thiếu district/city
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Pre-condition:**
  - Token: TOKEN_VALID
  - Data: BUNDLE_VALID_004
- **Steps:**
  1. Gọi API:
     Method: GET
     URL: /v1/bundles/BUNDLE_VALID_004
     Headers: { "Authorization": "Bearer TOKEN_VALID" }
     Params: { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "location.ward": "Dịch Vọng Hậu" }
  2. Quan sát response trả về
- **Expected Status:** 400  ← giả định; comment rõ trong code
- **Response Assertions:**
  - HTTP status 400 (ASSUMPTION — chờ confirm BA/DEV)
- **Blocked Note:** "Spec: không trả ra kết quả nếu thiếu điều kiện — cần xác nhận: trả 400 hay 200 không filter?"

---

---
```

---

### Step 6: Tạo file test_data_catalog.md

```markdown
# Test Data Catalog

> Tất cả data objects dùng trong test suite này.
> Điền giá trị thực vào `conftest.py` trước khi chạy.

## Tokens
| Object | Mô tả | Cách tạo |
|--------|-------|----------|
| TOKEN_VALID | Bearer token hợp lệ, còn hạn | Login lấy từ staging auth service |
| TOKEN_EXPIRED | Token đã hết hạn | Lấy token cũ hoặc mock |
| TOKEN_INVALID | Chuỗi ngẫu nhiên không hợp lệ | Hardcode: "INVALID_XYZ123" |
| TOKEN_NO_PERM | Token hợp lệ, role không có quyền | Tạo account role thấp trên staging |

## Bundle Objects
| Object | bundleId thực | Điều kiện DB cần đảm bảo |
|--------|--------------|--------------------------|
| BUNDLE_VALID_001 | [điền vào] | status=ACTIVE, có ≥1 dòng giá active+approved |
| BUNDLE_VALID_002 | [điền vào] | tương tự BUNDLE_VALID_001 |
| BUNDLE_INACTIVE_001 | [điền vào] | status=INACTIVE |
| BUNDLE_NO_VALID_PRICE_001 | [điền vào] | status=ACTIVE, tất cả dòng giá inactive/chưa approve |
| BUNDLE_WITH_DEVICE_001 | [điền vào] | có ≥1 SKU type=Physical (Thiết bị) |
| BUNDLE_NO_DEVICE_001 | [điền vào] | toàn bộ SKU type=Digital |
| BUNDLE_CYCLE_001 | [điền vào] | có Prepaid 3T, Prepaid 6T, Postpaid 1T |
| BUNDLE_BONUS_001 | [điền vào] | SKU có BONUS_MONTH config |
| BUNDLE_TIER_001 | [điền vào] | SKU có TIER_PRICE config |
| BUNDLE_LOCATION_001 | [điền vào] | có đúng 1 dòng giá active cho khu vực Nội thành HN |
| BUNDLE_MULTI_PRICE_001 | [điền vào] | nhiều dòng giá theo nhiều khu vực, giá khác nhau |
| BUNDLE_NOT_EXIST_001 | NON_EXISTENT_XYZ | không tồn tại trong DB |
...
```

---

### Step 7: Tạo file api_schema.md

```markdown
# API Schema — GET /v1/bundles/{bundleId}

## Request

**Method:** GET
**Base URL:** https://staging.tongdaiwifi.vn
**Path:** /v1/bundles/{bundleId}

### Path Parameters
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| bundleId | M | String | Mã gói bán |

### Query Parameters
| Field | Required | Type | Example | Description |
|-------|----------|------|---------|-------------|
| channelCode | M | String | FPT_WEB | Kênh gọi API |
| customerType | M | String | KH_MOI | Loại khách hàng |
| location.ward | O | String | "Dịch Vọng Hậu" | Phường/Xã |
| location.district | O | String | "Cầu Giấy" | Quận/Huyện |
| location.city | O | String | "Hà Nội" | Thành phố |
| cycle | O | Array[int] | [3, 6] | Filter theo chu kỳ (OR) |

### Headers
| Header | Required | Value |
|--------|----------|-------|
| Authorization | M | Bearer {token} |

## Response — Success (200)

```json
{
  "code": 0,
  "message": "string",
  "data": {
    "bundleId": "string",
    "bundleName": "string",
    "status": "ACTIVE|INACTIVE",
    "isEndToEndSelling": true,
    "customerType": "string",
    "paymentMethods": ["Online", "COD"],
    "Deploy": {
      "isRequired": true
    },
    "Bundletype": "Internet|FPT Play|...",
    "crosssellinglocation": 0,
    "PriceListBundle": [
      {
        "priceName": "string",
        "source": "ECOM",
        "status": "Active",
        "pricesummarylist": [
          {
            "totalserviceprice": { "paymenttype": "Prepaid", "cycle": 3, "totalprice": 480000 },
            "totaldeviceprice": { "paymenttype": "One time payment", "totalprice": 1200000 },
            "totalfeeprice": { "totalprice": 300000 }
          }
        ],
        "priceSKUList": [
          {
            "SKUid": "string",
            "SKUName": "string",
            "managementtype": "string",
            "priceSKUdetailList": [
              {
                "paymentmethod": "Prepaid",
                "cycle": 3,
                "unitPrice": 180000,
                "totalbaseprice": 540000,
                "totalfinalprice": 540000,
                "advancedPricingList": []
              }
            ]
          }
        ]
      }
    ],
    "SKUList": [ "..." ],
    "SKUGroupList": [ "..." ],
    "BundleDependencyRule": { "..." }
  }
}
```

## Business Rules (trích từ spec)

| ID | Rule |
|----|------|
| BR01 | Chỉ trả bundle có status=ACTIVE VÀ có ≥1 dòng giá active+đã phê duyệt |
| BR02 | Nếu truyền location đủ bộ 3: lấy giá theo khu vực. Nếu nhiều giá cùng khu vực: lấy giá thấp nhất |
| BR03 | Nếu không truyền location: trả giá thấp nhất toàn quốc |
| BR04 | location bắt buộc truyền đủ cặp ward-district-city; thiếu 1 → không trả kết quả |
| BR05 | cycle filter áp dụng OR condition; bỏ qua nếu paymentMethod = One Time Payment |
| BR06 | deploy.isRequired = true khi bundle có ≥1 SKU type=Physical |
| BR07 | channelCode scoping: chỉ trả bundle có dòng giá active cho channel đó |
```

---

### Step 8: Present output

In ra chat tóm tắt:

```
✅ Parse hoàn tất!

📊 Kết quả:
- Tổng TC đọc được: N
  - ✅ FULL (auto được): n TC
  - ⚠️ PARTIAL (một phần): n TC
  - ❌ SKIP (khó auto): n TC
- Data objects: N loại token, N loại bundle
- Blocked items cần confirm: N

📁 Files tạo ra:
- MEMORY.md
- test_scenario_map.md
- test_data_catalog.md
- api_schema.md

➡️ Bước tiếp theo: Gọi skill implement-auto-api để sinh code Playwright Python.
```

---

## Quy tắc quan trọng

- **KHÔNG sinh code Python/Playwright** ở bước này — chỉ parse và tạo Markdown
- **Giữ nguyên TC ID** từ file Excel (TC_GBD.1, TC_GBD.2...) — không tự đánh số lại
- **PARTIAL**: gen assertion dựa trên assumption hợp lý nhất, comment `# BLOCKED:` rõ ràng
- **SKIP**: ghi vào MEMORY.md nhưng KHÔNG tạo entry trong test_scenario_map.md
- **Blocked note**: copy nguyên văn từ cột Expected Result — không tóm tắt lại
- **Data objects**: extract từ cột Pre-condition, giữ đúng tên (BUNDLE_VALID_001 không đổi thành bundle_valid)

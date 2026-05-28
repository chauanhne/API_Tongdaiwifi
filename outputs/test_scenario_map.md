# Test Scenario Map — GET /v1/bundles/{bundleId}

> Chi tiết từng TC đã parse, dùng bởi implement-auto-api

---

## TC_GBD.1 — Happy path auth (token hợp lệ)
- **Group:** Authentication & Authorization
- **Priority:** High
- **Auto Tag:** FULL
- **Method:** GET
- **URL:** /v1/bundles/BUNDLE_VALID_001
- **Headers:** { "Authorization": "Bearer TOKEN_VALID", "Content-Type": "application/json" }
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
- **Expected Status:** 200
- **Response Assertions:**
  - `code` == 0
  - `data.bundleId` == bundle("BUNDLE_VALID_001")
  - `data.status` == "ACTIVE"
  - `data.PriceListBundle` length >= 1

---

## TC_GBD.2 — Không có header Authorization
- **Group:** Authentication & Authorization
- **Priority:** High
- **Auto Tag:** FULL
- **Method:** GET
- **URL:** /v1/bundles/BUNDLE_VALID_001
- **Headers:** { "Content-Type": "application/json" } (NO Authorization)
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
- **Expected Status:** 401
- **Response Assertions:**
  - `data` == null

---

## TC_GBD.3 — Token giả mạo
- **Group:** Authentication & Authorization
- **Priority:** High
- **Auto Tag:** FULL
- **Headers:** { "Authorization": "Bearer INVALID_XYZ123_FAKE" }
- **Expected Status:** 401

---

## TC_GBD.4 — Token hết hạn
- **Group:** Authentication & Authorization
- **Priority:** High
- **Auto Tag:** FULL
- **Headers:** { "Authorization": "Bearer TOKEN_EXPIRED" }
- **Expected Status:** 401

---

## TC_GBD.5 — Token không đủ quyền
- **Group:** Authentication & Authorization
- **Priority:** Medium
- **Auto Tag:** FULL
- **Headers:** { "Authorization": "Bearer TOKEN_NO_PERM" }
- **Expected Status:** 403

---

## TC_GBD.6 — Không có bundleId
- **Group:** Validate — Required Fields
- **Priority:** High
- **Auto Tag:** FULL
- **URL:** /v1/bundles/
- **Expected Status:** 404 hoặc 400

---

## TC_GBD.7 — bundleId không tồn tại
- **Group:** Validate — Required Fields
- **Priority:** High
- **Auto Tag:** FULL
- **URL:** /v1/bundles/NON_EXISTENT_BUNDLE_XYZ_999
- **Expected Status:** 404
- **Response Assertions:**
  - `data` == null

---

## TC_GBD.8 — Không có channelCode
- **Group:** Validate — Required Fields
- **Priority:** High
- **Auto Tag:** FULL
- **Params:** { "customerType": "KH_MOI" } (thiếu channelCode)
- **Expected Status:** 400

---

## TC_GBD.9 — channelCode không hợp lệ
- **Group:** Validate — Required Fields
- **Priority:** High
- **Auto Tag:** FULL
- **Params:** { "channelCode": "INVALID_CHANNEL_XYZ", "customerType": "KH_MOI" }
- **Expected Status:** 400 hoặc 404

---

## TC_GBD.10 — Không có customerType
- **Group:** Validate — Required Fields
- **Priority:** High
- **Auto Tag:** FULL
- **Params:** { "channelCode": "FPT_WEB" } (thiếu customerType)
- **Expected Status:** 400

---

## TC_GBD.11 — customerType không hợp lệ
- **Group:** Validate — Required Fields
- **Priority:** Medium
- **Auto Tag:** FULL
- **Params:** { "channelCode": "FPT_WEB", "customerType": "INVALID_TYPE_XYZ" }
- **Expected Status:** 400

---

## TC_GBD.12 — location thiếu district+city (PARTIAL)
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "location.ward": "Dịch Vọng Hậu" }
- **Expected Status:** 400 (ASSUMPTION)
- **Blocked Note:** "Spec: không trả ra kết quả nếu thiếu điều kiện — cần xác nhận: trả 400 hay 200 không filter?"

---

## TC_GBD.13 — location thiếu city (PARTIAL)
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "location.ward": "Dịch Vọng Hậu", "location.district": "Cầu Giấy" }
- **Expected Status:** 400 (ASSUMPTION)
- **Blocked Note:** "Confirm behavior khi thiếu 1 trong 3 location field"

---

## TC_GBD.14 — location thiếu ward (PARTIAL)
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "location.district": "Cầu Giấy", "location.city": "Hà Nội" }
- **Expected Status:** 400 (ASSUMPTION)
- **Blocked Note:** "Confirm behavior khi thiếu location.ward"

---

## TC_GBD.15 — cycle invalid format
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** FULL
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "cycle": ["abc"] }
- **Expected Status:** 400

---

## TC_GBD.16 — cycle=[3,6] OR condition
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_CYCLE_001
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "cycle": [3, 6] }
- **Expected Status:** 200
- **Response Assertions:**
  - Tất cả `priceSKUdetailList[].cycle` thuộc {3, 6} hoặc paymentmethod = "One Time Payment"
  - Không xuất hiện cycle 1T

---

## TC_GBD.17 — Không truyền cycle → trả toàn bộ
- **Group:** Validate — Format / Type
- **Priority:** Low
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_CYCLE_001
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
- **Expected Status:** 200
- **Response Assertions:**
  - Response trả đủ tất cả chu kỳ: 1T, 3T, 6T

---

## TC_GBD.18 — cycle bỏ qua với OTP bundle
- **Group:** Validate — Format / Type
- **Priority:** Medium
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_OTP_001
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI", "cycle": [3, 6] }
- **Expected Status:** 200
- **Response Assertions:**
  - PriceListBundle có dữ liệu (không bị filter rỗng)
  - `priceSKUdetailList[0].paymentmethod` == "One Time Payment"

---

## TC_GBD.19 — Bundle không có giá active (PARTIAL)
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_NO_VALID_PRICE_001
- **Expected Status:** 404
- **Blocked Note:** "Spec không chỉ định rõ: trả 404 hay 200 data rỗng?"

---

## TC_GBD.20 — Bundle INACTIVE (PARTIAL)
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_INACTIVE_001
- **Expected Status:** 404
- **Blocked Note:** "Confirm: trả 404 hay 200 data rỗng?"

---

## TC_GBD.21 — Không truyền location → giá thấp nhất toàn quốc
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_MULTI_PRICE_001
- **Params:** { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
- **Expected Status:** 200
- **Response Assertions:**
  - PriceListBundle trả 1 bảng giá (giá thấp nhất toàn quốc)
  - `priceSKUdetailList[0].totalfinalprice` == 480000

---

## TC_GBD.22 — Location đủ → đúng 1 giá khu vực
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_LOCATION_001
- **Params:** { "location.ward": "Dịch Vọng Hậu", "location.district": "Cầu Giấy", "location.city": "Hà Nội", ... }
- **Expected Status:** 200
- **Response Assertions:**
  - `priceSKUdetailList[0].totalfinalprice` == 550000

---

## TC_GBD.23 — Location đủ, nhiều giá → trả thấp nhất
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_MULTI_LOCATION_001
- **Params:** { "location.ward": "Dịch Vọng Hậu", "location.district": "Cầu Giấy", "location.city": "Hà Nội", ... }
- **Expected Status:** 200
- **Response Assertions:**
  - `priceSKUdetailList[0].totalfinalprice` == 480000

---

## TC_GBD.24 — deploy.isRequired=true
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_WITH_DEVICE_001
- **Expected Status:** 200
- **Response Assertions:**
  - `data.Deploy.isRequired` == true

---

## TC_GBD.25 — deploy.isRequired=false
- **Group:** Business Rule
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_NO_DEVICE_001
- **Expected Status:** 200
- **Response Assertions:**
  - `data.Deploy.isRequired` == false

---

## TC_GBD.26 — channelCode không match (PARTIAL)
- **Group:** Business Rule
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_APP_ONLY_001
- **Params:** { "channelCode": "FPT_WEB", ... }
- **Expected Status:** 404
- **Blocked Note:** "Confirm: trả 404 hay 200 data rỗng?"

---

## TC_GBD.27 — channelCode match
- **Group:** Business Rule
- **Priority:** Medium
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_APP_ONLY_001
- **Params:** { "channelCode": "APP", ... }
- **Expected Status:** 200

---

## TC_GBD.28 — crossselling (PARTIAL)
- **Group:** Business Rule
- **Priority:** Medium
- **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_CROSSSELL_001
- **Expected Status:** 200
- **Blocked Note:** "crosssellinglocation giá trị cụ thể là gì? (1/true/object)"

---

## TC_GBD.29 — cycle bỏ qua với OTP (BR03)
- **Group:** Business Rule
- **Priority:** Low
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_OTP_001
- **Params:** { "cycle": [3], ... }
- **Expected Status:** 200

---

## TC_GBD.30 — Full fields không null
- **Group:** Happy Path
- **Priority:** High
- **Auto Tag:** FULL
- **Bundle:** BUNDLE_FULL_001
- **Expected Status:** 200
- **Response Assertions:**
  - `data.bundleId`, `data.bundleName` != null
  - `data.status` == "ACTIVE"
  - `data.Deploy` != null
  - `data.PriceListBundle` length >= 1
  - `data.SKUList` length >= 1

---

## TC_GBD.31 — isEndToEndSelling=true
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_E2E_001 | **Expected:** `data.isEndToEndSelling` == true

## TC_GBD.32 — isEndToEndSelling=false
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_NON_E2E_001 | **Expected:** `data.isEndToEndSelling` == false

## TC_GBD.33 — pricesummarylist structure
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_PRICE_001
- **Expected:** pricesummarylist[0] có totalserviceprice, totaldeviceprice, totalfeeprice

## TC_GBD.34 — SKUList fields
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_SKU_001
- **Expected:** SKUList[0].{SKUid, type, IsMain, isRequired, MinQuantity, MaxQuantity, DefaultQuantity} != null

## TC_GBD.35 — BONUS_MONTH advancedPricing
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_BONUS_001
- **Expected:** advancedPricingList[0].type == "Tặng tháng", bonusMonths == 1, bonusType == "Phần trăm", bonusValue == 100

## TC_GBD.36 — TIER_PRICE advancedPricing
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_TIER_001
- **Expected:** advancedPricingList[0].type == "Đơn giá bậc thang", [1-5: 20000], [6-10: 15000]

## TC_GBD.37 — AttachmentFee structure
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_FEE_001
- **Expected:** AttachmentFee.{attachmentFeename, isRequired, DefaultQuantity} != null

## TC_GBD.38 — SKUGroupList IsOne=true
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_GROUP_SKU_001
- **Expected:** SKUGroupList[0].IsOne == true, SKUList length >= 1

## TC_GBD.39 — BundleDependencyRule
- **Group:** Happy Path | **Auto Tag:** FULL
- **Bundle:** BUNDLE_DEPENDENCY_001
- **Expected:** constraintItems[0].type thuộc {"Group","Simple","Fee"}, id != null

## TC_GBD.40 — paymentMethods (PARTIAL)
- **Group:** Happy Path | **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_PAYMENT_001
- **Expected:** paymentMethods is array, chứa "Online" và "COD"
- **Blocked Note:** "Danh sách đầy đủ giá trị hợp lệ?"

---

## TC_GBD.41 — State ACTIVE→INACTIVE (PARTIAL)
- **Group:** State Transition | **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_STATE_001
- **Steps:** Call lần 1 (ACTIVE) → Admin đổi INACTIVE → Call lần 2
- **Expected:** Lần 1: 200 | Lần 2: 404
- **Blocked Note:** "Cần quyền admin thực hiện bước 2; confirm cách thực hiện"

---

## TC_GBD.42 — Idempotent GET
- **Group:** Idempotency | **Auto Tag:** FULL
- **Bundle:** BUNDLE_IDEM_001
- **Expected:** response.data lần 1 == lần 2

---

## TC_GBD.43 — SQL injection
- **Group:** Error Handling | **Auto Tag:** FULL
- **URL:** /v1/bundles/1' OR '1'='1
- **Expected Status:** 400 hoặc 404 (KHÔNG phải 500), không lộ SQL error

## TC_GBD.44 — URL-encoded bundleId
- **Group:** Error Handling | **Auto Tag:** FULL
- **URL:** /v1/bundles/BUNDLE%20VALID
- **Expected Status:** 400 hoặc 404 (không phải 500)

## TC_GBD.45 — Content-Type header
- **Group:** Error Handling | **Auto Tag:** FULL
- **Expected:** Response header Content-Type chứa "application/json"

## TC_GBD.46 — Error không lộ stack trace
- **Group:** Error Handling | **Auto Tag:** FULL
- **URL:** /v1/bundles/NON_EXISTENT_BUNDLE_XYZ_999
- **Expected:** Response không chứa stack trace, class name, file path, DB query

## TC_GBD.47 — POST method → 405
- **Group:** Error Handling | **Auto Tag:** FULL
- **Method:** POST | **Expected Status:** 405

---

## TC_GBD.48, 49 — Performance (SKIP)
> SKIP: cần JMeter/k6. Không gen Playwright code.

## TC_GBD.50 — API vs DB data (PARTIAL)
- **Group:** Data Consistency | **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_CONSISTENCY_001
- **Expected:** API.data.bundleName == DB.bundleName, API.data.status == DB.status
- **Blocked Note:** "DB assertion cần thực hiện manual hoặc có DB fixture"

## TC_GBD.51 — Admin update → API reflect (PARTIAL)
- **Group:** Data Consistency | **Auto Tag:** PARTIAL
- **Bundle:** BUNDLE_CACHE_001
- **Blocked Note:** "Có cache TTL không? Bao lâu phản hồi data mới?"

---

## TC_GBD.52, 53 — Network/Timeout (SKIP)
> SKIP: cần Charles Proxy/Wireshark. Không gen Playwright code.

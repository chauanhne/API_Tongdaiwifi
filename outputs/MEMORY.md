# MEMORY — Parse TC Excel Output
> Tạo bởi: api-to-auto pipeline
> Ngày: 2026-05-21
> Dùng bởi: implement-auto-api

## 1. Project Info
- **Dự án:** ECOM Platform — Bundle API
- **Environment:** Staging
- **Base URL:** https://staging.tongdaiwifi.vn
- **API:** GET /v1/bundles/{bundleId}
- **Auth:** Bearer Token (header Authorization)
- **TC File:** outputs/AI_ClaudeCode_API_GetBundleDetail.xlsx

## 2. API Schema
- **Method:** GET
- **Endpoint:** /v1/bundles/{bundleId}
- **Required params:** bundleId (path), channelCode (query), customerType (query)
- **Optional params:** location.ward, location.district, location.city, cycle[] (array[int])
- **Response root:** { code: Int, message: String, data: BundleDetail }

> Chi tiết schema → xem `api_schema.md`

## 3. TC Summary
| Group | Tổng TC | FULL | PARTIAL | SKIP |
|-------|---------|------|---------|------|
| Authentication & Authorization | 5 | 5 | 0 | 0 |
| Validate — Required Fields | 6 | 6 | 0 | 0 |
| Validate — Format / Type | 7 | 4 | 3 | 0 |
| Business Rule | 11 | 7 | 4 | 0 |
| Happy Path & Data Integrity | 11 | 10 | 1 | 0 |
| State Transition | 1 | 0 | 1 | 0 |
| Idempotency | 1 | 1 | 0 | 0 |
| Error Handling | 5 | 5 | 0 | 0 |
| Performance / Rate Limit | 2 | 0 | 0 | 2 |
| Data Consistency | 2 | 0 | 2 | 0 |
| Network / Timeout | 2 | 0 | 0 | 2 |
| **TỔNG** | **53** | **38** | **11** | **4** |

## 4. TC Index (key entries)
| TC ID | Title ngắn | Group | Priority | Auto Tag | Blocked? |
|-------|-----------|-------|----------|----------|----------|
| TC_GBD.1 | Token hợp lệ → 200 | Authentication | High | FULL | — |
| TC_GBD.2 | Không có Authorization → 401 | Authentication | High | FULL | — |
| TC_GBD.3 | Token giả mạo → 401 | Authentication | High | FULL | — |
| TC_GBD.4 | Token hết hạn → 401 | Authentication | High | FULL | — |
| TC_GBD.5 | Token không đủ quyền → 403 | Authentication | Medium | FULL | — |
| TC_GBD.6 | Không có bundleId → 404 | Validate Req | High | FULL | — |
| TC_GBD.7 | bundleId không tồn tại → 404 | Validate Req | High | FULL | — |
| TC_GBD.8 | Không có channelCode → 400 | Validate Req | High | FULL | — |
| TC_GBD.9 | channelCode không hợp lệ → 400 | Validate Req | High | FULL | — |
| TC_GBD.10 | Không có customerType → 400 | Validate Req | High | FULL | — |
| TC_GBD.11 | customerType không hợp lệ → 400 | Validate Req | Medium | FULL | — |
| TC_GBD.12 | location thiếu district+city | Validate Fmt | Medium | PARTIAL | BLOCKED: 400 hay 200 bỏ qua? |
| TC_GBD.13 | location thiếu city | Validate Fmt | Medium | PARTIAL | BLOCKED |
| TC_GBD.14 | location thiếu ward | Validate Fmt | Medium | PARTIAL | BLOCKED |
| TC_GBD.15 | cycle invalid format → 400 | Validate Fmt | Medium | FULL | — |
| TC_GBD.16 | cycle=[3,6] OR condition | Validate Fmt | Medium | FULL | — |
| TC_GBD.17 | Không truyền cycle → trả hết | Validate Fmt | Low | FULL | — |
| TC_GBD.18 | cycle bỏ qua với OTP | Validate Fmt | Medium | FULL | — |
| TC_GBD.19 | Bundle không có giá active | Business Rule | High | PARTIAL | BLOCKED: 404 hay 200 empty? |
| TC_GBD.20 | Bundle INACTIVE | Business Rule | High | PARTIAL | BLOCKED: 404 hay 200 empty? |
| TC_GBD.21 | Không truyền location → giá thấp nhất | Business Rule | High | FULL | — |
| TC_GBD.22 | Location đủ → đúng 1 giá khu vực | Business Rule | High | FULL | — |
| TC_GBD.23 | Location đủ, nhiều giá → thấp nhất | Business Rule | High | FULL | — |
| TC_GBD.24 | deploy.isRequired=true (Physical SKU) | Business Rule | High | FULL | — |
| TC_GBD.25 | deploy.isRequired=false (Digital SKU) | Business Rule | High | FULL | — |
| TC_GBD.26 | channelCode không match → 404 | Business Rule | Medium | PARTIAL | BLOCKED |
| TC_GBD.27 | channelCode match → 200 | Business Rule | Medium | FULL | — |
| TC_GBD.28 | crossselling location | Business Rule | Medium | PARTIAL | BLOCKED: giá trị cụ thể? |
| TC_GBD.29 | cycle bỏ qua với OTP | Business Rule | Low | FULL | — |
| TC_GBD.30 | Full fields không null | Happy Path | High | FULL | — |
| TC_GBD.31-39 | Happy path details (E2E, pricesummary, SKU, advPricing…) | Happy Path | Medium | FULL | — |
| TC_GBD.40 | paymentMethods array | Happy Path | Medium | PARTIAL | BLOCKED: danh sách hợp lệ? |
| TC_GBD.41 | State ACTIVE→INACTIVE | State Transition | Medium | PARTIAL | BLOCKED: cần admin action |
| TC_GBD.42 | GET 2 lần → giống nhau | Idempotency | Medium | FULL | — |
| TC_GBD.43 | SQL injection → không 500 | Error Handling | High | FULL | — |
| TC_GBD.44-47 | Error handling cases | Error Handling | Medium | FULL | — |
| TC_GBD.48 | Response time SLA | Performance | Low | SKIP | BLOCKED: SLA threshold |
| TC_GBD.49 | 100 concurrent requests | Performance | Low | SKIP | BLOCKED: SLA concurrent |
| TC_GBD.50 | API data == DB data | Data Consistency | Medium | PARTIAL | PARTIAL: cần DB fixture |
| TC_GBD.51 | Admin update → API reflect | Data Consistency | Medium | PARTIAL | BLOCKED: cache TTL? |
| TC_GBD.52 | Network drop mid-request | Network | Low | SKIP | BLOCKED: tool simulate |
| TC_GBD.53 | Server timeout | Network | Low | SKIP | BLOCKED: threshold |

## 5. Data Objects Catalog
| Object | Dùng trong TC | Mô tả |
|--------|--------------|-------|
| TOKEN_VALID | hầu hết TC | Bearer token hợp lệ, còn hạn |
| TOKEN_INVALID | TC_GBD.3 | "INVALID_XYZ123_FAKE" |
| TOKEN_EXPIRED | TC_GBD.4 | Token đã hết hạn |
| TOKEN_NO_PERM | TC_GBD.5 | Role không đủ quyền |
| BUNDLE_VALID_001 | TC_GBD.1,2,3,4,5,6,8-11,15,30,43-47 | ACTIVE, ≥1 giá active, kênh FPT_WEB |
| BUNDLE_VALID_004 | TC_GBD.12,13,14 | ACTIVE, có giá khu vực |
| BUNDLE_NOT_EXIST_001 | TC_GBD.7,46 | "NON_EXISTENT_BUNDLE_XYZ_999" |
| BUNDLE_CYCLE_001 | TC_GBD.16,17 | Giá Prepaid 3T, 6T, Postpaid 1T |
| BUNDLE_OTP_001 | TC_GBD.18,29 | One Time Payment |
| BUNDLE_NO_VALID_PRICE_001 | TC_GBD.19 | ACTIVE, tất cả giá inactive/chưa approve |
| BUNDLE_INACTIVE_001 | TC_GBD.20 | status=INACTIVE |
| BUNDLE_MULTI_PRICE_001 | TC_GBD.21 | Nhiều giá theo khu vực, thấp nhất = 480K |
| BUNDLE_LOCATION_001 | TC_GBD.22 | 1 dòng giá khu vực Nội thành HN: 550K |
| BUNDLE_MULTI_LOCATION_001 | TC_GBD.23 | 2 giá cùng khu vực HN: 550K và 480K |
| BUNDLE_WITH_DEVICE_001 | TC_GBD.24 | ≥1 SKU type=Physical |
| BUNDLE_NO_DEVICE_001 | TC_GBD.25 | Tất cả SKU type=Digital |
| BUNDLE_APP_ONLY_001 | TC_GBD.26,27 | Chỉ có giá cho channel APP |
| BUNDLE_CROSSSELL_001 | TC_GBD.28 | Config cho phép bán chéo |
| BUNDLE_FULL_001 | TC_GBD.30 | Bundle đầy đủ config |
| BUNDLE_E2E_001 | TC_GBD.31 | isEndToEndSelling=true |
| BUNDLE_NON_E2E_001 | TC_GBD.32 | isEndToEndSelling=false |
| BUNDLE_PRICE_001 | TC_GBD.33 | service + device + fee price |
| BUNDLE_SKU_001 | TC_GBD.34 | SKU đầy đủ field |
| BUNDLE_BONUS_001 | TC_GBD.35 | BONUS_MONTH config |
| BUNDLE_TIER_001 | TC_GBD.36 | TIER_PRICE config |
| BUNDLE_FEE_001 | TC_GBD.37 | Có phí lắp đặt |
| BUNDLE_GROUP_SKU_001 | TC_GBD.38 | SKUGroupList, IsOne=true |
| BUNDLE_DEPENDENCY_001 | TC_GBD.39 | BundleDependencyRule |
| BUNDLE_PAYMENT_001 | TC_GBD.40 | paymentMethods=["Online","COD"] |
| BUNDLE_STATE_001 | TC_GBD.41 | Dùng test state transition |
| BUNDLE_IDEM_001 | TC_GBD.42 | Bundle stable idempotency |
| BUNDLE_PERF_001 | TC_GBD.48,49 | Performance test |
| BUNDLE_CONSISTENCY_001 | TC_GBD.50 | API vs DB compare |
| BUNDLE_CACHE_001 | TC_GBD.51 | Cache invalidation test |
| BUNDLE_NET_001 | TC_GBD.52,53 | Network/timeout test |

> Chi tiết → xem `test_data_catalog.md`

## 6. BLOCKED / Cần confirm
| TC ID | Vấn đề | Ảnh hưởng |
|-------|--------|-----------|
| TC_GBD.12 | location thiếu district+city: trả 400 hay 200 bỏ qua location? | PARTIAL |
| TC_GBD.13 | location thiếu city: trả 400 hay 200? | PARTIAL |
| TC_GBD.14 | location thiếu ward: trả 400 hay 200? | PARTIAL |
| TC_GBD.19 | Bundle không có giá active: trả 404 hay 200 data rỗng? | PARTIAL |
| TC_GBD.20 | Bundle INACTIVE: trả 404 hay 200 data rỗng? | PARTIAL |
| TC_GBD.26 | channelCode không match: trả 404 hay 200 data rỗng? | PARTIAL |
| TC_GBD.28 | crosssellinglocation giá trị cụ thể là gì? | PARTIAL |
| TC_GBD.40 | paymentMethods: danh sách đầy đủ các giá trị hợp lệ? | PARTIAL |
| TC_GBD.41 | State transition: cần quyền admin; confirm cách thực hiện | PARTIAL |
| TC_GBD.48 | SLA response time chính thức? | SKIP |
| TC_GBD.49 | SLA concurrent 95th percentile? | SKIP |
| TC_GBD.50 | DB assertion cần manual hoặc DB fixture | PARTIAL |
| TC_GBD.51 | Có cache TTL không? Bao lâu phản hồi data mới? | PARTIAL |
| TC_GBD.52 | Tool simulate network drop? | SKIP |
| TC_GBD.53 | Server timeout threshold chính thức? | SKIP |

## 7. File Reference
| File | Mô tả |
|------|-------|
| `MEMORY.md` | File này |
| `test_scenario_map.md` | Chi tiết từng TC đã parse |
| `test_data_catalog.md` | Tất cả data objects |
| `api_schema.md` | Request/response schema đầy đủ |
| `AI_ClaudeCode_API_GetBundleDetail.xlsx` | File TC gốc |

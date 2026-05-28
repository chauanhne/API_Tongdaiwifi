# Test Data Catalog

> Tất cả data objects dùng trong test suite GET /v1/bundles/{bundleId}
> Điền giá trị thực vào `conftest.py` trước khi chạy.

## Tokens
| Object | Mô tả | Cách tạo |
|--------|-------|----------|
| TOKEN_VALID | Bearer token hợp lệ, còn hạn, role=USER | Login staging auth service |
| TOKEN_EXPIRED | Token đã hết hạn | Lấy token cũ hoặc mock |
| TOKEN_INVALID | Chuỗi ngẫu nhiên: "INVALID_XYZ123_FAKE" | Hardcode |
| TOKEN_NO_PERM | Token hợp lệ, role không có quyền xem bundle | Tạo account role thấp trên staging |

## Bundle Objects
| Object | bundleId thực | Điều kiện DB cần đảm bảo |
|--------|--------------|--------------------------|
| BUNDLE_VALID_001 | [điền vào] | status=ACTIVE, ≥1 dòng giá active+approved, kênh FPT_WEB |
| BUNDLE_VALID_004 | [điền vào] | status=ACTIVE, có dòng giá khu vực |
| BUNDLE_NOT_EXIST_001 | NON_EXISTENT_BUNDLE_XYZ_999 | Không tồn tại trong DB |
| BUNDLE_CYCLE_001 | [điền vào] | Có giá Prepaid 3T, Prepaid 6T, Postpaid 1T |
| BUNDLE_OTP_001 | [điền vào] | paymentMethod = One Time Payment |
| BUNDLE_NO_VALID_PRICE_001 | [điền vào] | status=ACTIVE, tất cả dòng giá inactive/chưa approve |
| BUNDLE_INACTIVE_001 | [điền vào] | status=INACTIVE |
| BUNDLE_MULTI_PRICE_001 | [điền vào] | Nhiều dòng giá theo khu vực, giá thấp nhất toàn quốc = 480K |
| BUNDLE_LOCATION_001 | [điền vào] | Đúng 1 dòng giá khu vực Nội thành HN: 550K |
| BUNDLE_MULTI_LOCATION_001 | [điền vào] | 2 dòng giá cùng khu vực HN: 550K và 480K |
| BUNDLE_WITH_DEVICE_001 | [điền vào] | ≥1 SKU type=Physical (Thiết bị) |
| BUNDLE_NO_DEVICE_001 | [điền vào] | Tất cả SKU type=Digital |
| BUNDLE_APP_ONLY_001 | [điền vào] | Chỉ có dòng giá active cho channel APP (không có FPT_WEB) |
| BUNDLE_CROSSSELL_001 | [điền vào] | Config cho phép bán chéo |
| BUNDLE_FULL_001 | [điền vào] | Bundle đầy đủ config: SKU, giá, deploy, crosssell |
| BUNDLE_E2E_001 | [điền vào] | isEndToEndSelling=true |
| BUNDLE_NON_E2E_001 | [điền vào] | isEndToEndSelling=false |
| BUNDLE_PRICE_001 | [điền vào] | Có service price + device price + fee price |
| BUNDLE_SKU_001 | [điền vào] | SKU đầy đủ tất cả field bắt buộc |
| BUNDLE_BONUS_001 | [điền vào] | SKU có config tặng tháng (BONUS_MONTH): bonusMonths=1, PERCENT, 100% |
| BUNDLE_TIER_001 | [điền vào] | SKU có config giá bậc thang (TIER_PRICE): [1-5: 20K, 6-10: 15K] |
| BUNDLE_FEE_001 | [điền vào] | Bundle có phí đi kèm (Phí lắp đặt Internet) |
| BUNDLE_GROUP_SKU_001 | [điền vào] | Bundle có SKUGroupList với IsOne=true |
| BUNDLE_DEPENDENCY_001 | [điền vào] | Bundle có BundleDependencyRule cấu hình |
| BUNDLE_PAYMENT_001 | [điền vào] | paymentMethods=["Online", "COD"] |
| BUNDLE_STATE_001 | [điền vào] | Bundle dùng test state transition (ban đầu ACTIVE, có thể đổi INACTIVE) |
| BUNDLE_IDEM_001 | [điền vào] | Bundle stable, không thay đổi trong suốt test session |
| BUNDLE_PERF_001 | [điền vào] | Bundle dùng cho performance test (JMeter/k6) |
| BUNDLE_CONSISTENCY_001 | [điền vào] | Bundle dùng so sánh API vs DB (biết trước giá trị DB) |
| BUNDLE_CACHE_001 | [điền vào] | Bundle dùng test cache invalidation (có thể update tên) |
| BUNDLE_NET_001 | [điền vào] | Bundle dùng cho network/timeout test |

## Expected Values (điền sau khi biết bundleId thực)
| Object | Field | Expected Value |
|--------|-------|----------------|
| BUNDLE_MULTI_PRICE_001 | totalfinalprice (không location) | 480000 |
| BUNDLE_LOCATION_001 | totalfinalprice (khu vực Nội thành HN) | 550000 |
| BUNDLE_MULTI_LOCATION_001 | totalfinalprice (khu vực HN, min) | 480000 |
| BUNDLE_BONUS_001 | advancedPricingList[0].type | "Tặng tháng" |
| BUNDLE_BONUS_001 | advancedPricingList[0].bonusMonths | 1 |
| BUNDLE_TIER_001 | advancedPricingList[0].fromQty / toQty / unitPrice | 1 / 5 / 20000 |

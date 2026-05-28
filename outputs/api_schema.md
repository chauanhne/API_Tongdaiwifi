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
| location.city | O | String | "Hà Nội" | Thành phố/Tỉnh |
| cycle | O | Array[int] | [3, 6] | Filter chu kỳ (OR) |

### Headers
| Header | Required | Value |
|--------|----------|-------|
| Authorization | M | Bearer {token} |
| Content-Type | O | application/json |

## Business Rules
| ID | Rule |
|----|------|
| BR01 | Chỉ trả bundle có ≥1 dòng giá active+đã phê duyệt |
| BR02 | location phải truyền đủ bộ 3 (ward+district+city); thiếu 1 → không trả kết quả. Có location → lấy giá khu vực (nhiều → thấp nhất). Không có → giá thấp nhất toàn quốc |
| BR03 | cycle: OR condition, chỉ áp dụng Prepaid/Postpaid; bỏ qua nếu One Time Payment |
| BR04 | deploy.isRequired=true nếu ≥1 SKU type=Physical (Thiết bị) |
| BR05 | channelCode scoping: chỉ trả bundle có dòng giá active cho channel đó |

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
    "crosssellinglocation": 0,
    "Bundletype": "Internet|FPT Play|FPT Camera|...",
    "Deploy": {
      "isRequired": true
    },
    "SKUList": [
      {
        "SKUid": "string",
        "DisplayName": "string",
        "DisplayMode": "string",
        "IsMain": true,
        "isRequired": true,
        "serviceid": "string",
        "subservicetypeID": "string",
        "subserviceID": "string",
        "deploytypeID": "string",
        "revokeId": "string",
        "VatRate": "string",
        "type": "Physical|Digital",
        "PsID": "string",
        "ManagementMethod": "string",
        "Unit": "string",
        "ProductType": "string",
        "DeploymentVendor": "string",
        "MinQuantity": 1,
        "MaxQuantity": 999999999,
        "DefaultQuantity": 1,
        "AttachmentSKU": {
          "SKUName": "string",
          "Displayname": "string",
          "IsMain": true,
          "IsRequired": true,
          "DisplayMode": 1,
          "DefaultQuantity": 1,
          "MaxQuantity": 1,
          "MinQuantity": 1,
          "DeploymentVendorName": "TIN/PNC"
        },
        "AttachmentFee": {
          "attachmentFeename": "Phí lắp đặt Internet",
          "DisplayName": "string",
          "DisplayMode": "string",
          "isRequired": true,
          "serviceid": "string",
          "type": "Digital",
          "Ps_id": "string",
          "DeploymentVendorName": "string",
          "ManagementMethod": "string",
          "DefaultQuantity": 1,
          "MaxQuantity": 1,
          "MinQuantity": 1
        },
        "SKUAttributeList": [
          { "attributeName": "string", "attributeValue": "string" }
        ]
      }
    ],
    "SKUGroupList": [
      {
        "SKUgrouName": "string",
        "SKUgroupID": "string",
        "IsMain": true,
        "IsRequired": true,
        "IsOne": true,
        "SkuList": [
          {
            "SKUid": "string",
            "DisplayName": "string",
            "ManagementMethod": "string",
            "isRequired": true,
            "type": "Physical|Digital",
            "Ps_id": "string"
          }
        ]
      }
    ],
    "BundleDependencyRule": {
      "constraintItems": [
        { "type": "Group|Simple|Fee", "id": "string", "name": "string" }
      ],
      "restrictedItems": [
        { "type": "Group|Simple|Fee", "id": "string", "name": "string" }
      ],
      "dependencyType": "string",
      "ratio": "1:1"
    },
    "PriceListBundle": [
      {
        "priceName": "Giá bán khu vực HCM",
        "programID": "string",
        "source": "ECOM",
        "Policy_ID": "COMBO.1234",
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
            "SKUName": "FPT Play Max",
            "managementtype": "Dịch vụ Billing",
            "priceSKUdetailList": [
              {
                "paymentmethod": "Prepaid",
                "cycle": 3,
                "unitPrice": 180000,
                "totalbaseprice": 540000,
                "totalfinalprice": 540000,
                "advancedPricingList": [
                  {
                    "type": "Tặng tháng",
                    "bonusMonths": 1,
                    "bonusType": "Phần trăm",
                    "bonusValue": 100
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## Error Responses
| HTTP Code | Trigger khi nào |
|-----------|----------------|
| 400 | Thiếu required param, sai format |
| 401 | Không có/sai/hết hạn token |
| 403 | Token không đủ quyền |
| 404 | bundleId không tồn tại / bundle INACTIVE / không có giá hợp lệ |
| 405 | Method không phải GET |
| 500 | Lỗi server (không được xảy ra trong normal flow) |

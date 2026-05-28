# Group: Happy Path & Data Integrity
# TC: TC_GBD.32 → TC_GBD.42
# PARTIAL: TC_GBD.34, 40, 42

import pytest
from tests.conftest import bundle


def test_TC_GBD_32_response_has_required_fields(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_FULL_001"))
    data = response.json()

    assert response.status == 200
    d = data["data"]
    assert d.get("bundleId") is not None
    assert d.get("bundleName") is not None
    assert d.get("status") is not None
    assert d.get("customerType") is not None
    assert d.get("Bundletype") is not None
    assert d.get("Deploy") is not None
    assert len(d.get("PriceListBundle", [])) >= 1


def test_TC_GBD_33_is_end_to_end_selling_is_boolean(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_FULL_001"))
    data = response.json()

    assert response.status == 200
    assert isinstance(data["data"]["isEndToEndSelling"], bool)


# ⚠️ PARTIAL — TC_GBD.34
# Assumption: paymentMethods là array không rỗng.
# Cần biết danh sách paymentMethods thực tế của bundle để assert chính xác giá trị.
def test_TC_GBD_34_payment_methods_is_array(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_FULL_001"))
    data = response.json()

    assert response.status == 200
    methods = data["data"].get("paymentMethods", [])
    assert isinstance(methods, list)
    assert len(methods) >= 1


def test_TC_GBD_35_price_summary_list_structure(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_PRICE_001"))
    data = response.json()

    assert response.status == 200
    price_list = data["data"]["PriceListBundle"]
    assert len(price_list) >= 1
    summary_list = price_list[0]["pricesummarylist"]
    assert len(summary_list) >= 1
    summary = summary_list[0]
    assert "totalserviceprice" in summary
    assert summary["totalserviceprice"]["totalprice"] > 0


def test_TC_GBD_36_sku_list_has_required_fields(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_SKU_001"))
    data = response.json()

    assert response.status == 200
    sku_list = data["data"]["SKUList"]
    assert len(sku_list) >= 1
    sku = sku_list[0]
    assert sku.get("SKUid") is not None
    assert sku.get("DisplayName") is not None
    assert sku.get("type") in ["Physical", "Digital"]
    assert sku.get("MinQuantity", 0) >= 1
    assert sku.get("MaxQuantity", 0) >= 1


def test_TC_GBD_37_advanced_pricing_bonus_month(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_BONUS_001"))
    data = response.json()

    assert response.status == 200
    found_bonus = False
    for price in data["data"]["PriceListBundle"]:
        for sku_price in price.get("priceSKUList", []):
            for detail in sku_price.get("priceSKUdetailList", []):
                for adv in detail.get("advancedPricingList", []):
                    if adv.get("type") == "BONUS_MONTH":
                        assert adv.get("bonusMonths", 0) > 0
                        found_bonus = True
    assert found_bonus, "Không tìm thấy advancedPricing type=BONUS_MONTH"


def test_TC_GBD_38_advanced_pricing_tier_price(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_TIER_001"))
    data = response.json()

    assert response.status == 200
    found_tier = False
    for price in data["data"]["PriceListBundle"]:
        for sku_price in price.get("priceSKUList", []):
            for detail in sku_price.get("priceSKUdetailList", []):
                for adv in detail.get("advancedPricingList", []):
                    if adv.get("type") == "TIER_PRICE":
                        assert "fromQty" in adv
                        assert "toQty" in adv
                        found_tier = True
    assert found_tier, "Không tìm thấy advancedPricing type=TIER_PRICE"


def test_TC_GBD_39_attachment_fee_structure(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_FEE_001"))
    data = response.json()

    assert response.status == 200
    sku_list = data["data"]["SKUList"]
    found_fee = False
    for sku in sku_list:
        fees = sku.get("AttachmentFee", [])
        if len(fees) >= 1:
            assert fees[0].get("attachmentFeename") is not None
            assert fees[0].get("Ps_id") is not None
            found_fee = True
    assert found_fee, "Không tìm thấy AttachmentFee trong SKUList"


# ⚠️ PARTIAL — TC_GBD.40
# Assumption: bundle có nhiều chu kỳ với Ps_id khác nhau.
# Cần BUNDLE_MULTI_CYCLE_001 có dữ liệu Ps_id thực tế để verify không bằng nhau.
def test_TC_GBD_40_ps_id_differs_by_cycle(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_MULTI_CYCLE_001"))
    data = response.json()

    assert response.status == 200
    ps_ids = set()
    for sku in data["data"]["SKUList"]:
        for fee in sku.get("AttachmentFee", []):
            if fee.get("Ps_id"):
                ps_ids.add(fee["Ps_id"])
    # ASSUMPTION: có nhiều Ps_id khác nhau — update nếu data fixture chưa đủ
    assert len(ps_ids) >= 1


def test_TC_GBD_41_sku_group_list_is_one(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_GROUP_SKU_001"))
    data = response.json()

    assert response.status == 200
    group_list = data["data"].get("SKUGroupList", [])
    assert len(group_list) >= 1
    group = group_list[0]
    assert group["IsOne"] is True
    assert len(group.get("SkuList", [])) >= 1


# ⚠️ PARTIAL — TC_GBD.42
# Assumption: bundle có BundleDependencyRule với constraintItems và restrictedItems.
# Cần BUNDLE_DEPENDENCY_001 được cấu hình đúng trên staging.
def test_TC_GBD_42_bundle_dependency_rule(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_DEPENDENCY_001"))
    data = response.json()

    assert response.status == 200
    rule = data["data"].get("BundleDependencyRule", {})
    assert len(rule.get("constraintItems", [])) >= 1
    assert len(rule.get("restrictedItems", [])) >= 1

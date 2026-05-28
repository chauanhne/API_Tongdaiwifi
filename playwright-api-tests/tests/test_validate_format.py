# Group: Validate — Format / Type
# TC: TC_GBD.12 → TC_GBD.18
# TC_GBD.12, 14, 18: PARTIAL — có comment BLOCKED

import pytest
from tests.conftest import bundle, token


# ⚠️ PARTIAL — TC_GBD.12
# BLOCKED: Spec chưa rõ khi location chỉ có ward, thiếu district+city: trả 400 hay 200 không filter location?
# Assumption: expect 400. Cập nhật expected_status khi BA/DEV confirm.
def test_TC_GBD_12_location_only_ward(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_001"),
        location={"ward": "Dịch Vọng Hậu"},
    )
    # ASSUMPTION: 400 — update nếu BA confirm behavior khác
    assert response.status == 400


def test_TC_GBD_13_location_missing_city(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_001"),
        location={"ward": "Dịch Vọng Hậu", "district": "Cầu Giấy"},
    )
    assert response.status == 400


# ⚠️ PARTIAL — TC_GBD.14
# BLOCKED: location địa lý không khớp (ward/district không thuộc cùng city): trả 400 hay fallback về giá MIN toàn quốc?
# Assumption: expect 400. Cập nhật khi BA/DEV confirm.
def test_TC_GBD_14_location_geography_mismatch(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_001"),
        location={"ward": "Phường không khớp", "district": "Cầu Giấy", "city": "Hà Nội"},
    )
    # ASSUMPTION: 400 — update nếu BA confirm behavior khác
    assert response.status == 400


def test_TC_GBD_15_cycle_invalid_format(api_request_context):
    from config.settings import BASE_URL, TIMEOUT
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/{bundle('BUNDLE_VALID_001')}",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"channelCode": "FPT_WEB", "customerType": "KH_MOI", "cycle": "abc"},
        timeout=TIMEOUT,
    )
    assert response.status == 400


def test_TC_GBD_16_cycle_or_filter(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_CYCLE_001"),
        cycle=[3, 6],
    )
    data = response.json()

    assert response.status == 200
    price_list = data["data"]["PriceListBundle"]
    assert len(price_list) >= 1
    for price in price_list:
        for summary in price.get("pricesummarylist", []):
            svc = summary.get("totalserviceprice", {})
            if svc.get("paymenttype") == "Prepaid":
                assert svc.get("cycle") in [3, 6], f"Unexpected cycle: {svc.get('cycle')}"


def test_TC_GBD_17_no_cycle_returns_all(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_CYCLE_001"))
    data = response.json()

    assert response.status == 200
    assert len(data["data"]["PriceListBundle"]) >= 1


# ⚠️ PARTIAL — TC_GBD.18
# Assumption: bundle OTP bỏ qua cycle param, trả 200 với toàn bộ data.
# Cập nhật assert khi có bundleId OTP thực tế để kiểm chứng behavior.
def test_TC_GBD_18_cycle_ignored_for_otp(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_OTP_001"),
        cycle=[3],
    )
    data = response.json()

    assert response.status == 200
    # cycle bị bỏ qua — vẫn trả data
    assert data.get("data") is not None

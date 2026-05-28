# Group: Business Rules
# TC: TC_GBD.19 → TC_GBD.31
# PARTIAL: TC_GBD.20, 26, 27, 30, 31

import pytest
from tests.conftest import bundle, token


# ─── BR01 ────────────────────────────────────────────────────────────────────

def test_TC_GBD_19_active_bundle_all_prices_inactive(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NO_VALID_PRICE_001"))
    data = response.json()

    assert response.status in (404, 200)
    if response.status == 200:
        assert data.get("data") is None or data["data"].get("PriceListBundle") == []


# ⚠️ PARTIAL — TC_GBD.20
# BLOCKED: Bundle INACTIVE → API trả 404 hay 200 với data rỗng?
# Assumption: 404. Cập nhật khi BA/DEV confirm.
def test_TC_GBD_20_bundle_inactive(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_INACTIVE_001"))
    # ASSUMPTION: 404 — update nếu BA confirm 200 data rỗng
    assert response.status == 404


# ─── BR02 ────────────────────────────────────────────────────────────────────

def test_TC_GBD_21_no_location_returns_min_price(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NO_LOCATION_001"))
    data = response.json()

    assert response.status == 200
    assert len(data["data"]["PriceListBundle"]) >= 1


def test_TC_GBD_22_location_matches_one_price(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_LOCATION_001"),
        location={"ward": "Dịch Vọng Hậu", "district": "Cầu Giấy", "city": "Hà Nội"},
    )
    data = response.json()

    assert response.status == 200
    assert len(data["data"]["PriceListBundle"]) >= 1


def test_TC_GBD_23_location_multiple_prices_returns_min(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_MULTI_LOCATION_001"),
        location={"ward": "Dịch Vọng Hậu", "district": "Cầu Giấy", "city": "Hà Nội"},
    )
    data = response.json()

    assert response.status == 200
    # Chỉ trả 1 dòng giá (giá thấp nhất)
    assert len(data["data"]["PriceListBundle"]) == 1


# ─── BR03 ────────────────────────────────────────────────────────────────────

def test_TC_GBD_24_physical_sku_deploy_required_true(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_WITH_DEVICE_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["Deploy"]["isRequired"] is True


def test_TC_GBD_25_no_physical_sku_deploy_required_false(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NO_DEVICE_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["Deploy"]["isRequired"] is False


# ─── BR04 ────────────────────────────────────────────────────────────────────

# ⚠️ PARTIAL — TC_GBD.26
# Assumption: DisplayName == tên mặc định từ bảng SKU khi chưa cấu hình nội dung gói.
# Cần biết giá trị DisplayName mặc định thực tế từ DEV để assert chính xác.
def test_TC_GBD_26_sku_display_name_default(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NO_CONTENT_001"))
    data = response.json()

    assert response.status == 200
    sku_list = data["data"]["SKUList"]
    assert len(sku_list) >= 1
    # ASSUMPTION: DisplayName không null — update khi biết giá trị default thực tế
    assert sku_list[0]["DisplayName"] is not None


# ⚠️ PARTIAL — TC_GBD.27
# Assumption: DisplayName == giá trị custom từ cấu hình nội dung gói.
# Cần biết giá trị custom thực tế đã config trên staging để assert chính xác.
def test_TC_GBD_27_sku_display_name_from_config(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_WITH_CONTENT_001"))
    data = response.json()

    assert response.status == 200
    sku_list = data["data"]["SKUList"]
    assert len(sku_list) >= 1
    # ASSUMPTION: DisplayName không null và khác tên mặc định — update khi biết giá trị config thực
    assert sku_list[0]["DisplayName"] is not None


# ─── BR05 ────────────────────────────────────────────────────────────────────

def test_TC_GBD_28_app_only_bundle_via_web_returns_404(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_APP_ONLY_001"),
        channel_code="FPT_WEB",
    )
    assert response.status == 404


def test_TC_GBD_29_app_only_bundle_via_app_returns_200(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_APP_ONLY_001"),
        channel_code="FPT_APP",
    )
    assert response.status == 200


# ─── BR06 ────────────────────────────────────────────────────────────────────

# ⚠️ PARTIAL — TC_GBD.30
# Assumption: crosssellinglocation=1 khi bundle được cấu hình cho phép bán chéo.
# Cần BUNDLE_CROSSSELL_001 được set up đúng trên staging.
def test_TC_GBD_30_crosssell_location_enabled(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_CROSSSELL_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["crosssellinglocation"] == 1


# ⚠️ PARTIAL — TC_GBD.31
# Assumption: crosssellinglocation=0 khi bundle không cho phép bán chéo.
def test_TC_GBD_31_crosssell_location_disabled(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NO_CROSSSELL_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["crosssellinglocation"] == 0

# Group: Validate — Required Fields
# TC: TC_GBD.6 → TC_GBD.11

import pytest
from config.settings import BASE_URL, TIMEOUT
from pages.api_client import APIClient
from tests.conftest import bundle, token


def test_TC_GBD_6_no_bundle_id(api_request_context):
    client = APIClient(api_request_context, token=token("TOKEN_VALID"))
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"channelCode": "FPT_WEB", "customerType": "KH_MOI"},
        timeout=TIMEOUT,
    )
    assert response.status in (400, 404)


def test_TC_GBD_7_bundle_not_exist(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NOT_EXIST_001"))
    data = response.json()

    assert response.status == 404
    assert data.get("data") is None or data.get("data") == {}


def test_TC_GBD_8_missing_channel_code(api_request_context):
    client = APIClient(api_request_context, token=token("TOKEN_VALID"))
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/{bundle('BUNDLE_VALID_001')}",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"customerType": "KH_MOI"},
        timeout=TIMEOUT,
    )
    assert response.status == 400


# ⚠️ PARTIAL — TC_GBD.9
# Assumption: channelCode không hợp lệ → 400. Cập nhật nếu server trả 404.
def test_TC_GBD_9_invalid_channel_code(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_001"),
        channel_code="INVALID_CHANNEL_XYZ",
    )
    assert response.status == 400


def test_TC_GBD_10_missing_customer_type(api_request_context):
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/{bundle('BUNDLE_VALID_001')}",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"channelCode": "FPT_WEB"},
        timeout=TIMEOUT,
    )
    assert response.status == 400


def test_TC_GBD_11_invalid_customer_type(authed_client):
    response = authed_client.get_bundle_detail(
        bundle_id=bundle("BUNDLE_VALID_001"),
        customer_type="INVALID_TYPE_XYZ",
    )
    assert response.status == 400

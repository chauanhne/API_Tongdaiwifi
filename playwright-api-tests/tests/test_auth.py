# Group: Authentication & Authorization
# TC: TC_GBD.1 → TC_GBD.5

import pytest
from pages.api_client import APIClient
from tests.conftest import bundle, token


def test_TC_GBD_1_happy_path_valid_token(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))
    data = response.json()

    assert response.status == 200
    assert data["data"]["bundleId"] == bundle("BUNDLE_VALID_001")
    assert data["data"]["status"] == "ACTIVE"
    assert len(data["data"]["PriceListBundle"]) >= 1


def test_TC_GBD_2_no_authorization_header(api_request_context):
    client_no_token = APIClient(api_request_context, token=None)
    response = client_no_token.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401


def test_TC_GBD_3_invalid_token(api_request_context):
    client_invalid = APIClient(api_request_context, token=token("TOKEN_INVALID"))
    response = client_invalid.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401


def test_TC_GBD_4_expired_token(api_request_context):
    client_expired = APIClient(api_request_context, token=token("TOKEN_EXPIRED"))
    response = client_expired.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 401


def test_TC_GBD_5_token_no_permission(api_request_context):
    client_no_perm = APIClient(api_request_context, token=token("TOKEN_NO_PERM"))
    response = client_no_perm.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 403

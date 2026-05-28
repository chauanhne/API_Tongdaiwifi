# Group: Error Handling
# TC: TC_GBD.45 → TC_GBD.49

import pytest
from config.settings import BASE_URL, TIMEOUT
from tests.conftest import bundle, token


def test_TC_GBD_45_sql_injection_bundle_id(api_request_context):
    injection_id = "1' OR '1'='1"
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/{injection_id}",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"channelCode": "FPT_WEB", "customerType": "KH_MOI"},
        timeout=TIMEOUT,
    )
    assert response.status in (400, 404), f"Unexpected status: {response.status}"
    assert response.status != 500, "Server không được trả 500 khi nhận SQL injection input"

    body = response.text()
    sensitive_keywords = ["SQLException", "stack trace", "at line", "SELECT ", "FROM ", "syntax error"]
    for keyword in sensitive_keywords:
        assert keyword.lower() not in body.lower(), f"Response lộ thông tin nhạy cảm: '{keyword}'"


def test_TC_GBD_46_whitespace_bundle_id(api_request_context):
    response = api_request_context.get(
        f"{BASE_URL}/v1/bundles/%20",
        headers={"Authorization": f"Bearer {token('TOKEN_VALID')}"},
        params={"channelCode": "FPT_WEB", "customerType": "KH_MOI"},
        timeout=TIMEOUT,
    )
    assert response.status in (400, 404)


def test_TC_GBD_47_response_content_type_json(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 200
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, f"Expected application/json, got: {content_type}"


def test_TC_GBD_48_error_response_no_sensitive_info(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_NOT_EXIST_001"))

    assert response.status == 404
    body = response.text()
    sensitive_keywords = ["stack", "trace", "SQLException", "at line", "SELECT ", "NullPointerException"]
    for keyword in sensitive_keywords:
        assert keyword.lower() not in body.lower(), f"Response lộ thông tin nhạy cảm: '{keyword}'"


def test_TC_GBD_49_wrong_http_method_post(api_request_context):
    from pages.api_client import APIClient
    client = APIClient(api_request_context, token=token("TOKEN_VALID"))
    response = client.post_bundle_detail(bundle_id=bundle("BUNDLE_VALID_001"))

    assert response.status == 405

# tests/voucher/test_auth.py
# Group: Authentication & Authorization
# TC: TC_GLV.1 → TC_GLV.7
#
# NOTE: API luon tra HTTP 200, bao loi qua body: {success: false, error: {code, message}}
# Khong dung HTTP 4xx cho loi auth/validation.

import pytest
from tests.voucher.conftest import token, client_id
from pages.voucher_client import VoucherClient


# ── TC_GLV.1 ──────────────────────────────────────────────────────────────
# BUG: API tra success=false voi error CHECKOUT_PAYMENT_REQUIRED
# Can checkout token cua session da chon phuong thuc thanh toan
def test_TC_GLV_1_all_valid_headers_returns_success(full_client):
    # Pre-condition: TOKEN_CHECKOUT_VALID, TOKEN_AUTH_VALID, CLIENT_ID_VALID
    response = full_client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    # BUG: success=false, error.code=CHECKOUT_PAYMENT_REQUIRED
    # Checkout token nay chua chon payment method -> can token moi
    # Dang assert actual behavior de track bug
    assert data["success"] is True, (
        f"BUG [CHECKOUT_PAYMENT_REQUIRED]: "
        f"API tra success=false. error={data.get('error')}. "
        f"Can checkout token da chon payment method."
    )
    assert data["error"] is None
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


# ── TC_GLV.2 ──────────────────────────────────────────────────────────────
def test_TC_GLV_2_missing_authorization_returns_error(api_ctx):
    # Pre-condition: khong co Authorization header
    # NOTE: API khong validate Authorization doc lap, loi phu thuoc checkout state
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=None,
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"] is not None


# ── TC_GLV.3 ──────────────────────────────────────────────────────────────
def test_TC_GLV_3_invalid_authorization_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_INVALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False


# ── TC_GLV.4 ──────────────────────────────────────────────────────────────
def test_TC_GLV_4_expired_authorization_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_EXPIRED"),
    )
    response = client.get_list_voucher()

    assert response.status == 200
    assert response.json()["success"] is False


# ── TC_GLV.5 ──────────────────────────────────────────────────────────────
def test_TC_GLV_5_missing_checkout_token_returns_CHECKOUT_TOKEN_REQUIRED(api_ctx):
    # API validate X-Checkout-Token → tra error.code = CHECKOUT_TOKEN_REQUIRED
    client = VoucherClient(
        api_ctx,
        checkout_token=None,
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"]["code"] == "CHECKOUT_TOKEN_REQUIRED"


# ── TC_GLV.6 ──────────────────────────────────────────────────────────────
def test_TC_GLV_6_invalid_checkout_token_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_INVALID"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"] is not None


# ── TC_GLV.7 ──────────────────────────────────────────────────────────────
def test_TC_GLV_7_expired_checkout_token_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_EXPIRED"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"] is not None

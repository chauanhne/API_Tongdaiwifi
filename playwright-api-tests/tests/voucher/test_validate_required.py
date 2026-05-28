# tests/voucher/test_validate_required.py
# Group: Validate — Required Fields
# TC: TC_GLV.8 → TC_GLV.10
#
# NOTE: API luon tra HTTP 200, bao loi qua body.
# X-Checkout-Token la header duy nhat duoc validate doc lap.
# Authorization va Client-Id khong validate rieng → loi phu thuoc checkout state.

from tests.voucher.conftest import token, client_id
from pages.voucher_client import VoucherClient


# ── TC_GLV.8 ──────────────────────────────────────────────────────────────
# NOTE: Thieu Client-Id → API van xu ly, loi phu thuoc checkout state
# Khong tra 400/403 nhu expected — API khong validate Client-Id doc lap
def test_TC_GLV_8_missing_client_id_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=None,
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"] is not None


# ── TC_GLV.9 ──────────────────────────────────────────────────────────────
def test_TC_GLV_9_invalid_client_id_returns_error(api_ctx):
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=client_id("CLIENT_ID_INVALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"] is not None


# ── TC_GLV.10 ─────────────────────────────────────────────────────────────
def test_TC_GLV_10_no_headers_at_all_returns_CHECKOUT_TOKEN_REQUIRED(api_ctx):
    # Thieu X-Checkout-Token → error.code = CHECKOUT_TOKEN_REQUIRED
    client = VoucherClient(
        api_ctx,
        checkout_token=None,
        client_id=None,
        auth_token=None,
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200
    assert data["success"] is False
    assert data["error"]["code"] == "CHECKOUT_TOKEN_REQUIRED"

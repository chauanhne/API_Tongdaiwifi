# tests/voucher/test_error_handling.py
# Group: Error Handling
# TC: TC_GLV.15 → TC_GLV.16

from config.settings import ORDERING_BASE_URL, TIMEOUT
from tests.voucher.conftest import token, client_id


# ── TC_GLV.15 ─────────────────────────────────────────────────────────────
def test_TC_GLV_15_get_method_returns_405(api_ctx):
    # API validate HTTP method → GET tra 405 (khong phai 200)
    # Day la truong hop duy nhat API tra HTTP status khac 200
    response = api_ctx.get(
        f"{ORDERING_BASE_URL}/ordering/public/v1/voucher/list",
        headers={
            "X-Checkout-Token": token("TOKEN_CHECKOUT_VALID"),
            "Client-Id": client_id("CLIENT_ID_VALID"),
            "Authorization": f"Bearer {token('TOKEN_AUTH_VALID')}",
        },
        timeout=TIMEOUT,
    )
    assert response.status == 405


# ── TC_GLV.16 ─────────────────────────────────────────────────────────────
def test_TC_GLV_16_error_response_has_no_stack_trace(api_ctx):
    # API tra 200 + success=false cho loi auth — kiem tra body khong lo thong tin noi bo
    response = api_ctx.post(
        f"{ORDERING_BASE_URL}/ordering/public/v1/voucher/list",
        headers={
            "X-Checkout-Token": "INVALID_CHECKOUT_XYZ123",
            "Client-Id": client_id("CLIENT_ID_VALID"),
            "Authorization": "Bearer INVALID_XYZ123",
            "Content-Type": "application/json",
        },
        timeout=TIMEOUT,
    )
    body = response.text()

    assert response.status == 200
    data = response.json()
    assert data["success"] is False

    for leak in ("Traceback", "at com.", "NullPointerException",
                 "StackTrace", "System.Exception", "SELECT ", "FROM "):
        assert leak not in body, f"Server leak: {leak!r} trong response"

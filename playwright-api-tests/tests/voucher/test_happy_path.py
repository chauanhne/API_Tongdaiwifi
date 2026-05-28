# tests/voucher/test_happy_path.py
# Group: Happy Path & Data Integrity
# TC: TC_GLV.11 → TC_GLV.14
#
# NOTE: TC_GLV.11-14 can checkout token cua session da chon payment method.
# Hien tai TOKEN_CHECKOUT_VALID tra CHECKOUT_PAYMENT_REQUIRED.
# Cac test nay se PASS khi duoc cap checkout token hop le.

import re
from datetime import datetime
from tests.voucher.conftest import token, client_id
from pages.voucher_client import VoucherClient

REQUIRED_ITEM_FIELDS = [
    "voucher_code", "description", "note", "to_date",
    "register_type_id", "voucher_type",
    "policy_group_id", "apply_type_id", "promotion_type_id",
]


def _get_valid_data(full_client):
    """Helper: goi API va tra ve data[], assert truoc."""
    response = full_client.get_list_voucher()
    body = response.json()
    assert response.status == 200, f"HTTP {response.status}"
    assert body["success"] is True, (
        f"BUG: success=false. error={body.get('error')}. "
        "Can checkout token da chon payment method."
    )
    return body


# ── TC_GLV.11 ─────────────────────────────────────────────────────────────
def test_TC_GLV_11_response_structure_is_correct(full_client):
    body = _get_valid_data(full_client)

    assert body["error"] is None
    assert isinstance(body["data"], list)
    meta = body["meta"]
    assert meta["request_id"] not in (None, "")
    assert meta["trace_id"] not in (None, "")
    assert meta["timestamp"] not in (None, "")


# ── TC_GLV.12 ─────────────────────────────────────────────────────────────
def test_TC_GLV_12_each_voucher_item_has_9_required_fields(full_client):
    body = _get_valid_data(full_client)
    items = body["data"]
    assert len(items) >= 1

    for item in items:
        for field in REQUIRED_ITEM_FIELDS:
            assert field in item, f"Thieu field: {field}"
            assert item[field] is not None, f"Field null: {field}"
        assert isinstance(item["voucher_code"], str) and item["voucher_code"] != ""
        assert isinstance(item["register_type_id"], int)
        assert isinstance(item["policy_group_id"], int)
        assert isinstance(item["apply_type_id"], int)
        assert isinstance(item["promotion_type_id"], int)


# ── TC_GLV.13 ─────────────────────────────────────────────────────────────
def test_TC_GLV_13_checkout_with_no_vouchers_returns_empty_list(api_ctx):
    # Can TOKEN_CHECKOUT_VALID_NO_VOUCHER (checkout hop le, khong co voucher)
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID_NO_VOUCHER"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    body = response.json()

    assert response.status == 200
    assert body["success"] is True, (
        f"BUG: success=false. error={body.get('error')}"
    )
    assert body["data"] == [], f"Expected data=[], got {body['data']}"


# ── TC_GLV.14 ─────────────────────────────────────────────────────────────
def test_TC_GLV_14_to_date_format_is_dd_mm_yyyy(full_client):
    body = _get_valid_data(full_client)
    pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")

    for item in body["data"]:
        to_date = item["to_date"]
        assert pattern.match(to_date), f"to_date format sai: {to_date!r}"
        day, month, year = to_date.split("/")
        datetime(int(year), int(month), int(day))

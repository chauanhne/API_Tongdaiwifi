# tests/voucher/test_idempotency.py
# Group: Idempotency / Duplicate Request
# TC: TC_GLV.17


# ── TC_GLV.17 ─────────────────────────────────────────────────────────────
def test_TC_GLV_17_two_identical_calls_return_same_data(full_client):
    # Pre-condition: TOKEN_CHECKOUT_VALID, TOKEN_AUTH_VALID, CLIENT_ID_VALID,
    #                CHECKOUT_WITH_VOUCHERS (khong thay doi giua 2 lan goi)
    resp1 = full_client.get_list_voucher()
    resp2 = full_client.get_list_voucher()

    assert resp1.status == 200
    assert resp2.status == 200

    data1 = resp1.json()["data"]
    data2 = resp2.json()["data"]
    assert data1 == data2, "data khac nhau giua 2 lan goi"

    # request_id phai khac nhau (moi request la unique)
    rid1 = resp1.json()["meta"]["request_id"]
    rid2 = resp2.json()["meta"]["request_id"]
    assert rid1 != rid2, f"request_id trung lap: {rid1}"

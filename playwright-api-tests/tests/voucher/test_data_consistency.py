# tests/voucher/test_data_consistency.py
# Group: Data Consistency
# TC: TC_GLV.18

from datetime import datetime
from tests.voucher.conftest import token, client_id
from pages.voucher_client import VoucherClient


# ── TC_GLV.18 ─────────────────────────────────────────────────────────────
# ⚠️ PARTIAL — TC_GLV.18
# BLOCKED: Spec khong noi ro — API co filter voucher het han (to_date < today) ra khoi list khong?
# Assumption: voucher het han KHONG xuat hien trong data. Cap nhat khi BA/DEV confirm.
def test_TC_GLV_18_expired_voucher_not_in_list(api_ctx):
    # Pre-condition: TOKEN_CHECKOUT_VALID_WITH_EXPIRED_VOUCHER
    #                DB: CHECKOUT_WITH_EXPIRED_VOUCHER (to_date da qua ngay hien tai)
    client = VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID_WITH_EXPIRED_VOUCHER"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )
    response = client.get_list_voucher()
    data = response.json()

    assert response.status == 200

    today = datetime.today()
    for item in data["data"]:
        to_date_str = item["to_date"]  # format dd/MM/yyyy
        day, month, year = to_date_str.split("/")
        to_date = datetime(int(year), int(month), int(day))
        # ASSUMPTION: khong co voucher het han trong list
        assert to_date >= today, (
            f"Voucher het han xuat hien trong list: voucher_code={item['voucher_code']!r}, "
            f"to_date={to_date_str!r}"
        )

# TC_GLV.19 — Performance / Rate Limit: SKIP
# Dung JMeter/k6 de test concurrent load — khong gen Playwright cho TC nay.

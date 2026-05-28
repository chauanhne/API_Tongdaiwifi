# pages/voucher_client.py
from playwright.sync_api import APIRequestContext
from config.settings import ORDERING_BASE_URL, TIMEOUT


class VoucherClient:
    def __init__(
        self,
        request: APIRequestContext,
        checkout_token: str = None,
        client_id: str = "tongdaiwifi",
        auth_token: str = None,
    ):
        self.request       = request
        self.checkout_token = checkout_token
        self.client_id     = client_id
        self.auth_token    = auth_token

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.checkout_token is not None:
            h["X-Checkout-Token"] = self.checkout_token
        if self.client_id is not None:
            h["Client-Id"] = self.client_id
        if self.auth_token is not None:
            h["Authorization"] = f"Bearer {self.auth_token}"
        return h

    def get_list_voucher(self):
        """POST /ordering/public/v1/voucher/list"""
        return self.request.post(
            f"{ORDERING_BASE_URL}/ordering/public/v1/voucher/list",
            headers=self._headers(),
            timeout=TIMEOUT,
        )

from playwright.sync_api import APIRequestContext
from config.settings import BASE_URL, TIMEOUT


class APIClient:
    def __init__(self, request: APIRequestContext, token: str = None):
        self.request = request
        self.token = token

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_bundle_detail(
        self,
        bundle_id: str,
        channel_code: str = "FPT_WEB",
        customer_type: str = "KH_MOI",
        location: dict = None,
        cycle: list = None,
    ):
        """GET /v1/bundles/{bundleId}"""
        params = {
            "channelCode": channel_code,
            "customerType": customer_type,
        }
        if location:
            params.update({
                "location.ward": location.get("ward"),
                "location.district": location.get("district"),
                "location.city": location.get("city"),
            })
            params = {k: v for k, v in params.items() if v is not None}
        if cycle:
            params["cycle"] = cycle

        return self.request.get(
            f"{BASE_URL}/v1/bundles/{bundle_id}",
            headers=self._headers(),
            params=params,
            timeout=TIMEOUT,
        )

    def post_bundle_detail(self, bundle_id: str, channel_code: str = "FPT_WEB", customer_type: str = "KH_MOI"):
        """POST /v1/bundles/{bundleId} — dùng để test TC_GBD.49 (wrong method)"""
        return self.request.post(
            f"{BASE_URL}/v1/bundles/{bundle_id}",
            headers=self._headers(),
            params={"channelCode": channel_code, "customerType": customer_type},
            timeout=TIMEOUT,
        )

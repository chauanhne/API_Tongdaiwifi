import pytest
from playwright.sync_api import Playwright
from pages.api_client import APIClient


# ─── Tokens ────────────────────────────────────────────────────────────────
# TODO: Điền giá trị thực từ môi trường staging trước khi chạy
TOKENS = {
    "TOKEN_VALID":   "REPLACE_WITH_REAL_TOKEN",
    "TOKEN_EXPIRED": "REPLACE_WITH_EXPIRED_TOKEN",
    "TOKEN_INVALID": "INVALID_XYZ123_FAKE_TOKEN",
    "TOKEN_NO_PERM": "REPLACE_WITH_LOW_ROLE_TOKEN",
}

# ─── Bundle IDs ─────────────────────────────────────────────────────────────
# TODO: Điền bundleId thực từ DB staging
BUNDLE_IDS = {
    "BUNDLE_VALID_001":             "REPLACE_WITH_REAL_BUNDLE_ID",
    "BUNDLE_NOT_EXIST_001":         "NON_EXISTENT_BUNDLE_XYZ_999",
    "BUNDLE_NO_VALID_PRICE_001":    "REPLACE_WITH_BUNDLE_NO_VALID_PRICE",
    "BUNDLE_INACTIVE_001":          "REPLACE_WITH_INACTIVE_BUNDLE_ID",
    "BUNDLE_NO_LOCATION_001":       "REPLACE_WITH_BUNDLE_MULTI_NATIONAL_PRICE",
    "BUNDLE_LOCATION_001":          "REPLACE_WITH_BUNDLE_SINGLE_LOCATION_PRICE",
    "BUNDLE_MULTI_LOCATION_001":    "REPLACE_WITH_BUNDLE_MULTI_LOCATION_PRICE",
    "BUNDLE_WITH_DEVICE_001":       "REPLACE_WITH_BUNDLE_WITH_PHYSICAL_SKU",
    "BUNDLE_NO_DEVICE_001":         "REPLACE_WITH_BUNDLE_ALL_DIGITAL",
    "BUNDLE_NO_CONTENT_001":        "REPLACE_WITH_BUNDLE_NO_CONTENT_CONFIG",
    "BUNDLE_WITH_CONTENT_001":      "REPLACE_WITH_BUNDLE_WITH_CONTENT_CONFIG",
    "BUNDLE_APP_ONLY_001":          "REPLACE_WITH_BUNDLE_APP_CHANNEL_ONLY",
    "BUNDLE_CROSSSELL_001":         "REPLACE_WITH_BUNDLE_CROSSSELL_ALLOWED",
    "BUNDLE_NO_CROSSSELL_001":      "REPLACE_WITH_BUNDLE_CROSSSELL_NOT_ALLOWED",
    "BUNDLE_FULL_001":              "REPLACE_WITH_BUNDLE_FULL_DATA",
    "BUNDLE_PRICE_001":             "REPLACE_WITH_BUNDLE_PRICE_ALL_TYPES",
    "BUNDLE_SKU_001":               "REPLACE_WITH_BUNDLE_MIXED_SKU",
    "BUNDLE_BONUS_001":             "REPLACE_WITH_BUNDLE_BONUS_MONTH",
    "BUNDLE_TIER_001":              "REPLACE_WITH_BUNDLE_TIER_PRICE",
    "BUNDLE_FEE_001":               "REPLACE_WITH_BUNDLE_WITH_ATTACHMENT_FEE",
    "BUNDLE_MULTI_CYCLE_001":       "REPLACE_WITH_BUNDLE_FEE_MULTI_CYCLE",
    "BUNDLE_GROUP_SKU_001":         "REPLACE_WITH_BUNDLE_SKU_GROUP",
    "BUNDLE_DEPENDENCY_001":        "REPLACE_WITH_BUNDLE_WITH_DEPENDENCY_RULE",
    "BUNDLE_STATE_001":             "REPLACE_WITH_BUNDLE_FOR_STATE_TEST",
    "BUNDLE_IDEM_001":              "REPLACE_WITH_BUNDLE_FOR_IDEMPOTENCY",
    "BUNDLE_CYCLE_001":             "REPLACE_WITH_BUNDLE_MULTI_CYCLE",
    "BUNDLE_OTP_001":               "REPLACE_WITH_BUNDLE_ONE_TIME_PAYMENT",
    "BUNDLE_CONSISTENCY_001":       "REPLACE_WITH_BUNDLE_FOR_CONSISTENCY_TEST",
    "BUNDLE_SKU_CONSISTENCY_001":   "REPLACE_WITH_BUNDLE_SKU_CONSISTENCY",
    "BUNDLE_CACHE_001":             "REPLACE_WITH_BUNDLE_FOR_CACHE_TEST",
}


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright):
    context = playwright.request.new_context(base_url="https://staging.tongdaiwifi.vn")
    yield context
    context.dispose()


@pytest.fixture
def client(api_request_context):
    """APIClient không có token"""
    return APIClient(api_request_context)


@pytest.fixture
def authed_client(api_request_context):
    """APIClient với TOKEN_VALID"""
    return APIClient(api_request_context, token=TOKENS["TOKEN_VALID"])


def bundle(name: str) -> str:
    return BUNDLE_IDS[name]


def token(name: str) -> str:
    return TOKENS[name]

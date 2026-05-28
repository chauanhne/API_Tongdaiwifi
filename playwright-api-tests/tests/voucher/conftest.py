# tests/voucher/conftest.py
import pytest
from playwright.sync_api import Playwright
from pages.voucher_client import VoucherClient
from config.settings import ORDERING_BASE_URL

TOKENS = {
    "TOKEN_CHECKOUT_VALID":                      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGVja291dElkIjoiMDAwMEkyUTVLMFBTIiwianRpIjoiOTk0MTJjMmEtYWZhNy00MDgyLTkyNDAtNGE2MmRmYzAyMDVkIiwibmJmIjoxNzc5OTU0OTExLCJleHAiOjE3Nzk5NTYxMTEsImlhdCI6MTc3OTk1NDkxMX0.HIzJOaO-DHoGTSxJi3pupedER_qBj6QU_BF_ugOzVQA",
    "TOKEN_CHECKOUT_EXPIRED":                    "REPLACE_WITH_EXPIRED_CHECKOUT_TOKEN",
    "TOKEN_CHECKOUT_INVALID":                    "INVALID_CHECKOUT_XYZ123",
    "TOKEN_CHECKOUT_VALID_NO_VOUCHER":           "REPLACE_WITH_CHECKOUT_TOKEN_NO_VOUCHER",
    "TOKEN_CHECKOUT_VALID_WITH_EXPIRED_VOUCHER": "REPLACE_WITH_CHECKOUT_TOKEN_WITH_EXPIRED_VOUCHER",
    "TOKEN_AUTH_VALID":                          "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhNTRkNzgxNi02MGU3LTQwMDAtYWMwYi0zNTI1MDdiM2E4OGQiLCJjbGllbnRfaWQiOiI3Yzg5ZjI3Yi0yMjYwLTQ1MzItOGJkOC00ZTQ4NDIwYTBiNDgiLCJjbGllbnRfdHlwZSI6ImludGVybmFsIiwiY2hhbm5lbF9pZCI6IjEiLCJzY29wZSI6IiIsIm5iZiI6MTc3OTk1NDg1MywiZXhwIjoxNzgwODE4ODUzLCJpYXQiOjE3Nzk5NTQ4NTMsImlzcyI6ImVjcC1wbGF0Zm9ybSIsImF1ZCI6ImVjcC1wbGF0Zm9ybSJ9.1D_El9ze3pcwkD4Q6Tv-g6Cg5nR8AOfmNYpftXR4QvY",
    "TOKEN_AUTH_EXPIRED":                        "REPLACE_WITH_EXPIRED_AUTH_TOKEN",
    "TOKEN_AUTH_INVALID":                        "INVALID_XYZ123_FAKE_TOKEN",
}

CLIENT_IDS = {
    "CLIENT_ID_VALID":   "tongdaiwifi",
    "CLIENT_ID_INVALID": "INVALID_CLIENT_XYZ",
}


def token(name: str) -> str:
    return TOKENS[name]


def client_id(name: str) -> str:
    return CLIENT_IDS[name]


@pytest.fixture(scope="session")
def api_ctx(playwright: Playwright):
    ctx = playwright.request.new_context(base_url=ORDERING_BASE_URL)
    yield ctx
    ctx.dispose()


@pytest.fixture
def full_client(api_ctx):
    """VoucherClient với tất cả 3 headers hợp lệ"""
    return VoucherClient(
        api_ctx,
        checkout_token=token("TOKEN_CHECKOUT_VALID"),
        client_id=client_id("CLIENT_ID_VALID"),
        auth_token=token("TOKEN_AUTH_VALID"),
    )

# Group: Data Consistency
# TC: TC_GBD.52 → TC_GBD.54
# TC_GBD.52: FULL (cần DB fixture)
# TC_GBD.53, 54: PARTIAL

import pytest
from tests.conftest import bundle


# DB assertions cần DB connection fixture riêng
# TODO: Setup db_connection fixture trong conftest.py hoặc file conftest riêng
# Ví dụ: import psycopg2 / pymysql và query staging DB


def test_TC_GBD_52_api_data_matches_db(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_CONSISTENCY_001"))
    data = response.json()

    assert response.status == 200
    d = data["data"]
    assert d.get("bundleId") == bundle("BUNDLE_CONSISTENCY_001")
    assert d.get("status") == "ACTIVE"

    # DB: verify manually
    # expected_name = db.query("SELECT bundle_name FROM bundles WHERE bundle_id = %s", bundle_id)
    # assert d["bundleName"] == expected_name
    # expected_type = db.query("SELECT bundle_type FROM bundles WHERE bundle_id = %s", bundle_id)
    # assert d["Bundletype"] == expected_type
    pytest.skip("TC_GBD.52: Cần DB fixture để verify bundleName, status, Bundletype vs DB — setup DB connection trước")


# ⚠️ PARTIAL — TC_GBD.53
# Assumption: SKUList[*].SKUid và DisplayName khớp DB.
# Cần DB connection fixture để query và compare.
def test_TC_GBD_53_sku_list_matches_db(authed_client):
    response = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_SKU_CONSISTENCY_001"))
    data = response.json()

    assert response.status == 200
    sku_list = data["data"].get("SKUList", [])
    assert len(sku_list) >= 1

    # DB: verify manually
    # for sku in sku_list:
    #     db_sku = db.query("SELECT sku_name FROM skus WHERE sku_id = %s", sku["SKUid"])
    #     assert sku["DisplayName"] == db_sku["sku_name"]
    pytest.skip("TC_GBD.53: Cần DB fixture để verify SKUList vs DB")


# ⚠️ PARTIAL — TC_GBD.54
# BLOCKED: Cache TTL và invalidation mechanism chưa được confirm từ DEV.
# Assumption: sau khi admin update bundleName, response tiếp theo phải trả tên mới.
def test_TC_GBD_54_data_fresh_after_admin_update(authed_client):
    # Step 1: Gọi API lần 1 → lấy bundleName hiện tại
    response_before = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_CACHE_001"))
    assert response_before.status == 200
    name_before = response_before.json()["data"]["bundleName"]

    # Step 2: Admin update bundleName (cần thực hiện thủ công hoặc gọi admin API)
    # TODO: Gọi admin API hoặc update DB trực tiếp
    pytest.skip(
        "TC_GBD.54: Cần admin update bundleName trên staging rồi verify response mới. "
        "BLOCKED: Cache TTL chưa confirm — hỏi DEV về cache invalidation."
    )

    # Step 3: Gọi API lần 2 → bundleName phải đã thay đổi (cache invalidated)
    # response_after = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_CACHE_001"))
    # assert response_after.status == 200
    # assert response_after.json()["data"]["bundleName"] != name_before

# Group: Idempotency
# TC: TC_GBD.44

from tests.conftest import bundle


def test_TC_GBD_44_idempotent_get(authed_client):
    resp1 = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_IDEM_001"))
    resp2 = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_IDEM_001"))

    assert resp1.status == 200
    assert resp2.status == 200
    assert resp1.json()["data"] == resp2.json()["data"]

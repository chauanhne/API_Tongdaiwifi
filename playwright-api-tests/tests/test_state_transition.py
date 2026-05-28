# Group: State Transition
# TC: TC_GBD.43
# ⚠️ PARTIAL — cần admin action giữa 2 lần gọi API

import pytest
from tests.conftest import bundle


# ⚠️ PARTIAL — TC_GBD.43
# BLOCKED: Cần admin/DB action để set bundle INACTIVE giữa 2 bước.
# Step 1 tự động được. Step 2 (set INACTIVE) cần thao tác thủ công hoặc DB fixture.
# Assumption: sau khi INACTIVE → API trả 404.
@pytest.mark.partial
def test_TC_GBD_43_state_active_to_inactive(authed_client):
    # Step 1: Bundle đang ACTIVE → gọi API lần 1 → expect 200
    response_before = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_STATE_001"))
    assert response_before.status == 200, "Pre-condition: bundle phải ACTIVE trước khi test"

    # Step 2: Admin/DB cần set BUNDLE_STATE_001 → INACTIVE
    # TODO: Thực hiện thủ công hoặc thêm DB fixture ở đây
    pytest.skip("TC_GBD.43: Cần admin set bundle INACTIVE — chạy thủ công bước 2 rồi uncomment assert bên dưới")

    # Step 3: Gọi API lần 2 → expect 404
    # response_after = authed_client.get_bundle_detail(bundle_id=bundle("BUNDLE_STATE_001"))
    # assert response_after.status == 404

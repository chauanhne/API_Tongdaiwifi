---
name: auto-bug-capture
description: >
  Cấu hình Playwright Python tự động quay video + chụp screenshot + lưu trace
  khi test fail. Sinh ra file conftest.py với video recording config, và script
  collect_bugs.py để gom toàn bộ artifact (video, screenshot, error log) của
  các test fail vào thư mục bug-artifacts/ sau mỗi test run.
  Trigger khi user nhắc đến: "quay video khi test fail", "tự động quay bug",
  "playwright record video", "capture bug artifact", "lưu video lỗi",
  "setup video recording playwright", "cấu hình quay màn hình auto test",
  hoặc sau khi đã có project Playwright từ implement-auto-api và muốn bật
  tính năng capture bug. Skill này UPDATE conftest.py hiện có — không tạo mới.
---

# Auto Bug Capture — Playwright Video Recording

Cấu hình Playwright tự động quay video + screenshot + trace khi test fail,
và gom artifact vào cấu trúc chuẩn để `auto-bug-report` đọc sau.

---

## Vị trí trong Pipeline

```
implement-auto-api
  (tests/*.py, conftest.py)
        │
        ▼
★ auto-bug-capture ★
  (update conftest.py + sinh collect_bugs.py)
        │
        ▼
  pytest chạy → test fail → video/screenshot/trace tự lưu
        │
        ▼
  collect_bugs.py → bug-artifacts/
        │           bugs_summary.json (tc_id, error_message, timestamp)
        ▼
  auto-bug-report → đọc bugs_summary.json + test_scenario_map.md
        │           (Pre-condition + Steps tách biệt — template 8 cột)
        ▼
  bug_report.xlsx
```

---

## Cấu trúc output sau khi cấu hình

```
playwright-api-tests/
├── tests/
│   └── conftest.py              ← UPDATE: thêm video + trace config
├── scripts/
│   └── collect_bugs.py          ← MỚI: gom artifact sau test run
├── pytest.ini                   ← UPDATE: thêm --video, --screenshot flags
├── bug-artifacts/               ← Tạo khi chạy collect_bugs.py
│   ├── TC_GBD_3/
│   │   ├── video.webm           (video toàn bộ test case)
│   │   ├── screenshot.png       (screenshot tại thời điểm fail)
│   │   ├── trace.zip            (Playwright trace viewer)
│   │   └── error.json           (TC ID, error message, assertion failed)
│   ├── TC_GBD_12/
│   │   └── ...
│   └── bugs_summary.json        ← input cho auto-bug-report
```

---

## Workflow

### Step 1: Đọc conftest.py hiện có

Tìm file `tests/conftest.py` đã sinh bởi `implement-auto-api`.
Nếu không tìm thấy → báo user chạy `implement-auto-api` trước.

### Step 2: Update conftest.py

Thêm/thay thế `api_request_context` fixture để bật video + trace:

```python
# tests/conftest.py
# ─── THÊM VÀO ĐẦU FILE ────────────────────────────────────────────────
import json
import os
from pathlib import Path
from datetime import datetime

# ─── BUG ARTIFACT CONFIG ──────────────────────────────────────────────
ARTIFACT_DIR = Path("bug-artifacts")
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


# ─── THAY THẾ fixture api_request_context ─────────────────────────────
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Bật video recording cho toàn bộ session"""
    return {
        **browser_context_args,
        "record_video_dir": str(ARTIFACT_DIR / "raw_videos"),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright):
    """APIRequestContext với trace recording"""
    context = playwright.request.new_context(
        base_url="https://staging.tongdaiwifi.vn"
    )
    context.start_tracing(
        screenshots=True,
        snapshots=True,
        sources=True,
    )
    yield context
    context.stop_tracing(path=str(ARTIFACT_DIR / "raw_traces" / f"trace_{RUN_ID}.zip"))
    context.dispose()


# ─── HOOK: tự động capture khi test FAIL ──────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Extract TC ID từ tên function: test_TC_GBD_3_... → TC_GBD.3
        func_name = item.name
        tc_id = _extract_tc_id(func_name)
        bug_dir = ARTIFACT_DIR / tc_id
        bug_dir.mkdir(parents=True, exist_ok=True)

        # Lưu error info
        error_info = {
            "tc_id": tc_id,
            "function": func_name,
            "file": str(item.fspath),
            "run_id": RUN_ID,
            "timestamp": datetime.now().isoformat(),
            "error_message": str(report.longreprtext) if hasattr(report, "longreprtext") else str(report.longrepr),
            "phase": "call",
        }
        with open(bug_dir / "error.json", "w", encoding="utf-8") as f:
            json.dump(error_info, f, ensure_ascii=False, indent=2)

        # Screenshot (nếu có browser context)
        if hasattr(item, "_playwright_page"):
            try:
                item._playwright_page.screenshot(path=str(bug_dir / "screenshot.png"))
            except Exception:
                pass  # API test không có page — bỏ qua


def _extract_tc_id(func_name: str) -> str:
    """
    test_TC_GBD_3_invalid_token → TC_GBD.3
    test_TC_GBD_12_location_missing → TC_GBD.12
    """
    import re
    match = re.search(r"TC_([A-Z]+)_(\d+)", func_name)
    if match:
        return f"TC_{match.group(1)}.{match.group(2)}"
    return func_name  # fallback: dùng nguyên tên function


# ─── HOOK: tổng kết sau toàn bộ test run ─────────────────────────────
def pytest_sessionfinish(session, exitstatus):
    """Ghi bugs_summary.json sau khi chạy xong"""
    failed_tests = [
        report for report in session.testscollected
        if hasattr(report, "failed") and report.failed
    ]
    # Đọc tất cả error.json đã tạo
    bugs = []
    if ARTIFACT_DIR.exists():
        for error_file in ARTIFACT_DIR.glob("*/error.json"):
            with open(error_file, encoding="utf-8") as f:
                bugs.append(json.load(f))

    summary = {
        "run_id": RUN_ID,
        "timestamp": datetime.now().isoformat(),
        "total_bugs": len(bugs),
        "bugs": bugs,
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACT_DIR / "bugs_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
```

---

### Step 3: Sinh scripts/collect_bugs.py

Script chạy sau `pytest` để gom video vào đúng thư mục từng bug:

```python
# scripts/collect_bugs.py
"""
Chạy sau pytest để gom video Playwright vào thư mục bug-artifacts/<TC_ID>/

Usage:
    python scripts/collect_bugs.py

Playwright lưu video vào bug-artifacts/raw_videos/ với tên ngẫu nhiên.
Script này map video → TC_ID dựa theo timestamp gần nhất với error.json.
"""

import json
import shutil
import re
from pathlib import Path
from datetime import datetime


ARTIFACT_DIR = Path("bug-artifacts")
RAW_VIDEO_DIR = ARTIFACT_DIR / "raw_videos"


def collect():
    if not ARTIFACT_DIR.exists():
        print("❌ Chưa có bug-artifacts/. Chạy pytest trước.")
        return

    # Lấy tất cả bug dirs (có error.json)
    bug_dirs = sorted([d for d in ARTIFACT_DIR.iterdir()
                       if d.is_dir() and (d / "error.json").exists()])

    if not bug_dirs:
        print("✅ Không có bug nào. Tất cả test pass!")
        return

    print(f"🐛 Tìm thấy {len(bug_dirs)} bug(s). Đang gom artifact...")

    # Map video theo thứ tự thời gian
    videos = sorted(RAW_VIDEO_DIR.glob("*.webm"), key=lambda p: p.stat().st_mtime) \
             if RAW_VIDEO_DIR.exists() else []

    for i, bug_dir in enumerate(bug_dirs):
        with open(bug_dir / "error.json", encoding="utf-8") as f:
            error = json.load(f)

        tc_id = error["tc_id"]

        # Copy video tương ứng (theo thứ tự)
        if i < len(videos):
            dest = bug_dir / "video.webm"
            shutil.copy2(videos[i], dest)
            print(f"  📹 {tc_id}: video → {dest}")
        else:
            print(f"  ⚠️  {tc_id}: không tìm được video tương ứng")

        print(f"  📁 {tc_id}: {bug_dir}")

    print(f"\n✅ Hoàn tất. Xem artifact tại: {ARTIFACT_DIR}/")
    print(f"📊 Chạy tiếp: python scripts/generate_bug_report.py")
    print(f"   hoặc gọi skill auto-bug-report để sinh Excel bug report.")


if __name__ == "__main__":
    collect()
```

---

### Step 4: Update pytest.ini

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short --video=retain-on-failure --screenshot=only-on-failure --tracing=retain-on-failure
markers =
    full: TC auto hoàn toàn
    partial: TC auto một phần (có BLOCKED assumptions)
    skip_auto: TC không auto được (performance, network)
```

**Giải thích flags:**

| Flag | Ý nghĩa |
|------|---------|
| `--video=retain-on-failure` | Chỉ giữ video của test FAIL — xóa video test PASS để tiết kiệm disk |
| `--screenshot=only-on-failure` | Screenshot tại thời điểm fail |
| `--tracing=retain-on-failure` | Lưu trace.zip để mở bằng Playwright Trace Viewer |

---

### Step 5: Thêm vào requirements.txt

```
playwright>=1.44.0
pytest>=8.0.0
pytest-playwright>=0.5.0
python-dotenv>=1.0.0
```

> `pytest-playwright` đã tích hợp sẵn `--video`, `--screenshot`, `--tracing` flags — không cần thêm thư viện ngoài.

---

### Step 6: Present output + hướng dẫn

```
✅ Cấu hình video recording hoàn tất!

📋 Files đã update/tạo:
  - tests/conftest.py       (bật video + trace + hook capture)
  - scripts/collect_bugs.py (gom artifact sau test run)
  - pytest.ini              (thêm --video flags)

⚙️ Quy trình chạy:

  # Bước 1: Chạy test (video tự lưu khi fail)
  pytest tests/ -v

  # Bước 2: Gom video vào đúng thư mục bug
  python scripts/collect_bugs.py

  # Bước 3: Sinh Excel bug report
  → Gọi skill auto-bug-report

📁 Sau bước 2, cấu trúc artifact:
  bug-artifacts/
    TC_GBD.3/
      ├── video.webm       ← mở bằng trình duyệt/VLC
      ├── screenshot.png   ← ảnh tại thời điểm assert fail
      ├── trace.zip        ← mở bằng: playwright show-trace trace.zip
      └── error.json       ← error message + timestamp
    bugs_summary.json      ← input cho auto-bug-report
```

---

## Quy tắc quan trọng

- **KHÔNG tạo conftest.py mới** — chỉ UPDATE file hiện có từ `implement-auto-api`
- **Video chỉ giữ khi FAIL** (`retain-on-failure`) — test pass không tốn disk
- `bugs_summary.json` là **contract** giữa skill này và `auto-bug-report` — không đổi schema
- Nếu project chưa có `bug-artifacts/` → tạo tự động khi pytest chạy lần đầu

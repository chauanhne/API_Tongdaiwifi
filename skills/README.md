# 🧰 API Auto Test — Skill Pack

Bộ skill hoàn chỉnh cho quy trình **API Automation Testing** từ đầu đến cuối:
nhận link API spec → sinh TC → gen Playwright Python → chạy test → quay video bug → xuất Excel bug report.

---

## 📦 Danh sách Skills

| # | Skill | Loại | Mô tả ngắn |
|---|-------|------|------------|
| 1 | `testcase-api-writer` | UPDATE | Sinh TC `.xlsx` từ API spec. Đã bổ sung cột "Khả Năng Auto" |
| 2 | `parse-tc-excel` | MỚI | Đọc TC `.xlsx` + API spec `.xlsx` → MEMORY.md |
| 3 | `implement-auto-api` | MỚI | MEMORY.md → Playwright Python project |
| 4 | `auto-bug-capture` | MỚI | Config video recording khi test fail |
| 5 | `auto-bug-report` | MỚI | `bugs_summary.json` → Excel bug report chuẩn dự án |
| 6 | `api-to-auto` | MỚI | **Orchestrator** — chạy tất cả 4 phase tự động từ 1 link spec |

---

## 🗂️ Cách cài đặt

Copy từng thư mục skill vào `/mnt/skills/user/`:

```
/mnt/skills/user/
├── testcase-api-writer/   ← THAY THẾ file cũ bằng file trong pack này
│   └── SKILL.md
├── parse-tc-excel/        ← Thư mục mới
│   └── SKILL.md
├── implement-auto-api/    ← Thư mục mới
│   └── SKILL.md
├── auto-bug-capture/      ← Thư mục mới
│   └── SKILL.md
├── auto-bug-report/       ← Thư mục mới
│   └── SKILL.md
└── api-to-auto/           ← Thư mục mới
    └── SKILL.md
```

> ⚠️ `testcase-api-writer` là bản UPDATE — cần thay thế file cũ, không tạo thêm.

---

## 🚀 Cách sử dụng

### Option A — Full auto từ link spec (khuyến nghị)

```
Vợ nói: "Link spec: [url google sheet] → gen playwright đi"
```

Skill `api-to-auto` tự chạy **4 phase liên tiếp**:

```
Phase 1: testcase-api-writer  →  TC.xlsx
Phase 2: parse-tc-excel       →  MEMORY.md + analysis files
Phase 3: implement-auto-api   →  tests/*.py + conftest.py
Phase 4: auto-bug-capture     →  video config + collect_bugs.py
```

Sau khi pipeline xong, vợ tự chạy:
```bash
# 1. Điền token + bundleId thực vào conftest.py
# 2. Cài dependencies
pip install -r requirements.txt && playwright install

# 3. Chạy test (video tự lưu khi fail)
pytest tests/ -v

# 4. Gom video vào bug-artifacts/
python scripts/collect_bugs.py
```

Rồi gọi Claude: **"Gen bug report đi"** → skill `auto-bug-report` → `BugReport_*.xlsx`

---

### Option B — Chạy từng bước riêng lẻ

| Muốn làm gì | Gọi skill |
|-------------|-----------|
| Chỉ sinh TC từ link API spec | `testcase-api-writer` |
| Có TC Excel rồi, muốn gen Playwright | `parse-tc-excel` → `implement-auto-api` |
| Đã có project Playwright, muốn bật video | `auto-bug-capture` |
| Đã chạy pytest xong, muốn bug report | `auto-bug-report` |

---

## 🔄 Toàn bộ Flow

```
[Link API Spec]
      │
      ▼
  api-to-auto
  ├─ Phase 1 ─────────────────── testcase-api-writer
  │              AI_ClaudeCode_API_<Endpoint>.xlsx
  │
  ├─ Phase 2 ─────────────────── parse-tc-excel
  │              MEMORY.md
  │              test_scenario_map.md
  │              test_data_catalog.md
  │              api_schema.md
  │
  ├─ Phase 3 ─────────────────── implement-auto-api
  │              playwright-api-tests/
  │                config/settings.py
  │                pages/api_client.py
  │                tests/conftest.py      ← điền token + bundleId
  │                tests/test_auth.py
  │                tests/test_validate_*.py
  │                tests/test_business_rule.py
  │                tests/test_happy_path.py
  │                tests/test_*.py ...
  │                pytest.ini
  │                requirements.txt
  │
  └─ Phase 4 ─────────────────── auto-bug-capture
                 conftest.py (updated — video hooks)
                 pytest.ini (updated — --video flags)
                 scripts/collect_bugs.py

      │ [Vợ tự chạy]
      ▼
  pytest tests/ -v
  python scripts/collect_bugs.py

      │ [Gọi Claude]
      ▼
  auto-bug-report
      └─ BugReport_<API>_<date>.xlsx
           Bug ID, TC ID, Severity, Priority
           Steps, Expected, Actual (parse từ pytest)
           Attachments: video.webm + screenshot.png + trace.zip
```

---

## 📋 Contract giữa các Skills

| File | Tạo bởi | Đọc bởi |
|------|---------|---------|
| `AI_ClaudeCode_API_*.xlsx` | `testcase-api-writer` | `parse-tc-excel` |
| `MEMORY.md` | `parse-tc-excel` | `implement-auto-api`, `auto-bug-report` |
| `test_scenario_map.md` | `parse-tc-excel` | `implement-auto-api`, `auto-bug-report` |
| `test_data_catalog.md` | `parse-tc-excel` | `implement-auto-api` |
| `api_schema.md` | `parse-tc-excel` | `implement-auto-api` |
| `tests/conftest.py` | `implement-auto-api` | `auto-bug-capture` (update) |
| `pytest.ini` | `implement-auto-api` | `auto-bug-capture` (update) |
| `bug-artifacts/bugs_summary.json` | `auto-bug-capture` hooks + `collect_bugs.py` | `auto-bug-report` |
| `BugReport_*.xlsx` | `auto-bug-report` | QC review / gửi BA-DEV |

---

## ⚙️ Yêu cầu môi trường

```bash
Python       >= 3.10
playwright   >= 1.44.0
pytest       >= 8.0.0
pytest-playwright >= 0.5.0
openpyxl     >= 3.1.0
python-dotenv >= 1.0.0
```

---

## 📝 Ghi chú

- **Base URL mặc định**: `https://staging.tongdaiwifi.vn` — đổi trong `config/settings.py`
- **Bug ID prefix**: `AUTO-001` để phân biệt với bug manual `BUG-001`
- **TC PARTIAL** (`⚠️`): gen code nhưng có `# BLOCKED:` comment — cần confirm BA/DEV rồi update expected
- **TC SKIP** (`❌`): Performance (dùng JMeter/k6) và Network/Timeout (dùng Charles Proxy) — không gen Playwright
- **Video**: chỉ giữ khi FAIL (`retain-on-failure`) — test PASS xóa tự động

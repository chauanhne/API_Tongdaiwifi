---
name: api-to-auto
description: >
  Pipeline đầu-cuối: nhận link file mô tả API (Google Sheet/Docs/Swagger) →
  tự động chạy toàn bộ 3 bước: (1) sinh Test Case .xlsx bằng testcase-api-writer,
  (2) parse TC Excel thành MEMORY.md bằng parse-tc-excel, (3) sinh Playwright Python
  bằng implement-auto-api. Không cần user thao tác từng bước — chỉ cần cung cấp
  link spec là ra code chạy được. Trigger khi user nhắc đến: "từ spec API gen auto",
  "link api spec gen playwright", "gen test playwright từ link", "chạy full pipeline auto",
  "từ API doc ra code test luôn", "gen TC rồi gen code luôn", "auto từ đầu đến cuối",
  hoặc cung cấp link Google Sheet/Docs/Swagger + yêu cầu gen automation.
  Skill này GỌI tuần tự: testcase-api-writer → parse-tc-excel → implement-auto-api.
---

# API to Auto — Full Pipeline Orchestrator

Nhận link file mô tả API → chạy 3 skill tuần tự → xuất Playwright Python test suite.

---

## Tổng quan Pipeline

```
[Link API Spec]
      │
      ▼
┌─────────────────────────────────────────────┐
│ PHASE 1 — testcase-api-writer               │
│ Phân tích spec → Sinh TC .xlsx              │
│ Output: AI_ClaudeCode_API_<Endpoint>.xlsx   │
└─────────────────────────────────────────────┘
      │
      ▼  (tự động tiếp, không hỏi user)
┌─────────────────────────────────────────────┐
│ PHASE 2 — parse-tc-excel                    │
│ Đọc .xlsx TC + API spec → MEMORY.md         │
│ Output: MEMORY.md, test_scenario_map.md,    │
│         test_data_catalog.md, api_schema.md │
└─────────────────────────────────────────────┘
      │
      ▼  (tự động tiếp, không hỏi user)
┌─────────────────────────────────────────────┐
│ PHASE 3 — implement-auto-api                │
│ MEMORY.md → Playwright Python               │
│ Output: conftest.py, test_*.py,             │
│         api_client.py, settings.py          │
└─────────────────────────────────────────────┘
      │
      ▼
[Báo cáo tổng kết toàn pipeline]
```

---

## Đầu vào cần thiết

| Input | Bắt buộc? | Dạng |
|-------|-----------|------|
| Link API Spec | **Bắt buộc** | Google Sheet, Google Docs, Swagger URL, Postman link |
| Tên API / Function ID | **Bắt buộc** | Ví dụ: "Get Bundle Detail", "GBD" |
| Base URL môi trường | Nên có | Ví dụ: https://staging.tongdaiwifi.vn — nếu không có, để placeholder |
| Sheet name cụ thể | Nên có | Nếu spec là Google Sheet nhiều tab |

> Nếu thiếu Link API Spec → hỏi user ngay, không tiếp tục.
> Nếu thiếu Base URL → dùng placeholder `REPLACE_WITH_BASE_URL`, không chặn pipeline.

---

## Workflow chi tiết

### Step 0: Thu thập input & xác nhận

Khi nhận được link, in ra xác nhận ngắn trước khi bắt đầu:

```
🚀 Bắt đầu pipeline: API → Test Case → Playwright Python

📎 Link spec: [link]
📋 API: [tên API nếu đã biết]
🌐 Base URL: [URL / "sẽ dùng placeholder"]

Pipeline gồm 3 phase:
  Phase 1 → Sinh Test Case Excel (testcase-api-writer)
  Phase 2 → Parse TC thành MEMORY.md (parse-tc-excel)
  Phase 3 → Sinh Playwright Python (implement-auto-api)

Bắt đầu Phase 1...
```

---

### Step 1: PHASE 1 — Gọi testcase-api-writer

**Đọc và thực thi đầy đủ skill `testcase-api-writer`** với input là link spec đã nhận.

Lưu ý khi chạy phase này trong context pipeline:
- Thực hiện đầy đủ tất cả bước của testcase-api-writer (Bước 0 → 5)
- **KHÔNG dừng lại hỏi user** sau khi tạo xong TC (vì pipeline tự động chạy tiếp)
- Sau khi xuất .xlsx, **giữ lại toàn bộ dữ liệu TC đã parse trong memory** (không đọc lại file)
- In progress marker khi xong: `✅ Phase 1 hoàn tất — [N] TC đã sinh`

**Dữ liệu truyền sang Phase 2:**
- File .xlsx TC vừa tạo (path `/mnt/user-data/outputs/AI_ClaudeCode_API_<Endpoint>.xlsx`)
  - 8 cột chuẩn: QC/AI | TC ID | Priority | Nội Dung Test | Pre-condition/Test Data | Các Bước Thực Hiện | Kết Quả Mong Đợi | Khả Năng Auto
- API spec đã parse (giữ trong context — Phase 2 không cần đọc lại link)
- Tên endpoint, method, schema

---

### Step 2: PHASE 2 — Gọi parse-tc-excel

**Đọc và thực thi đầy đủ skill `parse-tc-excel`** với input từ Phase 1.

Lưu ý khi chạy trong context pipeline:
- Input file TC: file .xlsx vừa tạo ở Phase 1
- Input API spec: **dùng lại dữ liệu đã parse từ Phase 1** — không fetch lại link
- Chạy từ Step 2 → Step 8 của parse-tc-excel (bỏ Step 1 "Thu thập input" vì đã có)
- **KHÔNG dừng hỏi user** sau khi tạo xong MEMORY.md
- In progress marker khi xong: `✅ Phase 2 hoàn tất — MEMORY.md + 3 files đã tạo`

**Dữ liệu truyền sang Phase 3:**
- `MEMORY.md`
- `test_scenario_map.md` — mỗi TC có Pre-condition và Steps tách biệt
- `test_data_catalog.md`
- `api_schema.md`

---

### Step 3: PHASE 3 — Gọi implement-auto-api

**Đọc và thực thi đầy đủ skill `implement-auto-api`** với input từ Phase 2.

Lưu ý khi chạy trong context pipeline:
- Bỏ Step 0 "Kiểm tra prerequisite" (MEMORY.md đã có từ Phase 2)
- Chạy Step 1 → Step 7 của implement-auto-api
- In progress marker khi xong: `✅ Phase 3 hoàn tất — Playwright Python project đã sinh`

---

### Step 4: Báo cáo tổng kết pipeline

Sau khi cả 3 phase hoàn tất, in báo cáo tổng hợp:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PIPELINE HOÀN TẤT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 1 — Test Case Excel
   File: AI_ClaudeCode_API_<Endpoint>.xlsx
   Tổng TC: N | High: n | Medium: n | Low: n
   ✅ Auto được: n | ⚠️ Partial: n | ❌ Skip: n

🗂️ PHASE 2 — Analysis Files
   ├── MEMORY.md
   ├── test_scenario_map.md
   ├── test_data_catalog.md
   └── api_schema.md
   BLOCKED cần confirm: N items

🐍 PHASE 3 — Playwright Python
   playwright-api-tests/
   ├── config/settings.py
   ├── pages/api_client.py
   ├── tests/
   │   ├── conftest.py       ← ⚠️ Cần điền token + bundleId thực
   │   ├── test_auth.py                (n TC)
   │   ├── test_validate_required.py   (n TC)
   │   ├── test_validate_format.py     (n TC)
   │   ├── test_business_rule.py       (n TC)
   │   ├── test_happy_path.py          (n TC)
   │   ├── test_state_transition.py    (n TC)
   │   ├── test_idempotency.py         (n TC)
   │   ├── test_error_handling.py      (n TC)
   │   └── test_data_consistency.py    (n TC)
   ├── pytest.ini
   └── requirements.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️  CHECKLIST TRƯỚC KHI CHẠY TEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ 1. Mở conftest.py → điền giá trị thực cho TOKENS (TOKEN_VALID, TOKEN_EXPIRED...)
□ 2. Mở conftest.py → điền bundleId thực cho BUNDLE_IDS (lấy từ DB staging)
□ 3. Kiểm tra config/settings.py → BASE_URL đúng chưa
□ 4. pip install -r requirements.txt
□ 5. playwright install
□ 6. pytest tests/ -v --tb=short
□ 7. Review các TC có comment # ⚠️ PARTIAL → update expected sau khi confirm BA/DEV

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 BLOCKED ITEMS (cần confirm trước khi chạy PARTIAL TC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Liệt kê từ MEMORY.md section 6]
• TC_GBD.XX — [nội dung blocked]
• ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 FILES ĐÃ XUẤT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Gọi present_files với toàn bộ file output]
```

---

## Xử lý lỗi giữa các phase

### Lỗi Phase 1 (testcase-api-writer thất bại)
```
Nguyên nhân thường gặp:
- Link spec không đọc được (private, sai URL, quota)
- Spec quá ít thông tin (thiếu endpoint, thiếu schema)

Xử lý:
→ Dừng pipeline
→ Báo user: "Phase 1 gặp lỗi: [lý do]. Vợ kiểm tra link spec và thử lại nhé."
→ KHÔNG tiếp tục Phase 2, 3
```

### Lỗi Phase 2 (parse-tc-excel thất bại)
```
Nguyên nhân thường gặp:
- File .xlsx từ Phase 1 không đúng cấu trúc 8 cột chuẩn:
  QC/AI | TC ID | Priority | Nội Dung Test | Pre-condition/Test Data |
  Các Bước Thực Hiện | Kết Quả Mong Đợi | Khả Năng Auto
- TC quá ít (< 3 TC)
- Cột Pre-condition hoặc Các Bước Thực Hiện bị gộp/trống

Xử lý:
→ Dừng pipeline
→ Báo user: "Phase 2 gặp lỗi khi parse TC: [lý do]. File .xlsx Phase 1 đã sẵn sàng."
→ User có thể dùng file .xlsx thủ công, rồi gọi riêng parse-tc-excel
```

### Warning (không dừng pipeline)
```
Cảnh báo nhưng vẫn chạy tiếp:
- Tất cả TC đều SKIP → sinh conftest.py + cấu trúc project nhưng không có test function
- BLOCKED > 50% TC → cảnh báo "Nhiều TC cần confirm BA/DEV" trong báo cáo
- Base URL không có → dùng placeholder, cảnh báo trong checklist
```

---

## Quy tắc quan trọng

### O1 — Không hỏi user giữa chừng
Toàn bộ 3 phase chạy liên tục. Chỉ dừng khi:
- Thiếu link spec ngay từ đầu
- Phase 1 hoặc 2 thất bại hoàn toàn

### O2 — Dữ liệu truyền qua context, không đọc lại file
Phase 2 dùng lại parse kết quả của Phase 1 từ context — không fetch lại link Google Sheet.
Phase 3 dùng MEMORY.md vừa tạo — không re-parse TC Excel.

### O3 — Present file một lần duy nhất ở cuối
Không present file từng phase. Gom tất cả vào `present_files` cuối pipeline.

### O4 — Thứ tự present files
```
1. AI_ClaudeCode_API_<Endpoint>.xlsx   (Phase 1 — xem TC)
2. conftest.py                          (Phase 3 — cần điền ngay)
3. test_auth.py, test_validate_...      (Phase 3 — test files)
4. api_client.py                        (Phase 3 — helper)
5. MEMORY.md                            (Phase 2 — reference)
```

### O5 — Progress markers bắt buộc
In rõ khi bắt đầu và kết thúc mỗi phase giúp user theo dõi tiến trình khi pipeline chạy lâu.

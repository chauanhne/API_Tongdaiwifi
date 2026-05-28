---
name: auto-bug-report
description: >
  Đọc kết quả từ bug-artifacts/bugs_summary.json (output của auto-bug-capture)
  và test_scenario_map.md (output của parse-tc-excel), sau đó xuất file Excel
  bug report chuẩn format dự án FPT Telecom. Mỗi bug là 1 row với đầy đủ:
  Bug ID, Module, TC ID, Severity, Priority, Summary, Steps to Reproduce,
  Expected Result, Actual Result (lấy từ error message thực tế), link video/screenshot.
  Trigger khi user nhắc đến: "sinh bug report", "xuất bug excel", "report bug sau auto",
  "tổng hợp bug playwright", "gen bug report từ test fail", "báo cáo bug automation",
  "export bug report", "lấy bug từ test run", hoặc sau khi chạy pytest + collect_bugs.py
  và muốn có file Excel để review/gửi BA/DEV. BẮT BUỘC có bugs_summary.json trước.
---

# Auto Bug Report — Excel từ Playwright Test Results

Đọc artifact từ `auto-bug-capture` → xuất Excel bug report chuẩn dự án.

---

## Vị trí trong Pipeline

```
pytest chạy (có auto-bug-capture config)
        │  test fail → video + screenshot + error.json
        ▼
collect_bugs.py → bug-artifacts/bugs_summary.json
        │
        ▼
★ auto-bug-report ★
        │  đọc bugs_summary.json + test_scenario_map.md
        ▼
BugReport_<API>_<date>.xlsx
```

---

## Đầu vào cần thiết

| Input | Bắt buộc? | Nguồn |
|-------|-----------|-------|
| `bug-artifacts/bugs_summary.json` | **Bắt buộc** | Output của `auto-bug-capture` sau pytest |
| `test_scenario_map.md` | Nên có | Output của `parse-tc-excel` — để lấy Expected Result gốc |
| `api_schema.md` | Nên có | Output của `parse-tc-excel` — để điền Module/Endpoint |

> Nếu không có `bugs_summary.json` → báo user chạy pytest + collect_bugs.py trước.
> Nếu không có `test_scenario_map.md` → vẫn gen được, nhưng Expected Result lấy từ error log.

---

## Cấu trúc file Excel output

### Tên file
```
BugReport_<TênAPI>_<YYYYMMDD>.xlsx
Ví dụ: BugReport_GetBundleDetail_20260521.xlsx
```

### Columns (9 cột — chuẩn dự án)

| # | Cột | Nội dung | Nguồn |
|---|-----|---------|-------|
| A | **Bug ID** | AUTO-001, AUTO-002... | Tự đánh số |
| B | **TC ID** | TC_GBD.3, TC_GBD.12... | `error.json` → `tc_id` |
| C | **Module / Endpoint** | Bundle Detail — GET /v1/bundles/{bundleId} | `api_schema.md` |
| D | **Summary** | `[Module] <mô tả hành vi sai ngắn gọn>` | Parse từ error message |
| E | **Severity** | Critical / Major / Minor / Trivial | Logic tự đánh giá (xem bên dưới) |
| F | **Priority** | High / Medium / Low | Dựa trên Priority TC gốc |
| G | **Steps to Reproduce** | Method + URL + Params/Body + Headers | `test_scenario_map.md` → Steps |
| H | **Expected Result** | HTTP status + response fields | `test_scenario_map.md` → Expected |
| I | **Actual Result** | Error message thực tế từ pytest | `error.json` → `error_message` |
| J | **Attachments** | Tên file video + screenshot (hyperlink) | `bug-artifacts/<TC_ID>/` |
| K | **Status** | `New` (mặc định khi mới gen) | Hardcode |
| L | **Note** | PARTIAL flag, BLOCKED note nếu có | `test_scenario_map.md` |

### Rows đặc biệt

- **Header row** (row 1): nền `#1F3864` (xanh navy), chữ trắng, bold
- **Bug row**: nền trắng xen `#F2F2F2` (zebra stripe mỗi 2 dòng)
- **Severity = Critical**: tô đỏ `#FF0000` cột E
- **Severity = Major**: tô cam `#FF6600` cột E
- **PARTIAL bug** (từ TC `⚠️`): cột L tô vàng `#FFF2CC`, ghi BLOCKED note

---

## Workflow

### Step 1: Kiểm tra prerequisite

```python
# Kiểm tra bugs_summary.json
if not Path("bug-artifacts/bugs_summary.json").exists():
    → Báo: "Chưa có bugs_summary.json. Vợ chạy pytest rồi python scripts/collect_bugs.py trước nhé."
    → DỪNG

# Đọc số bug
with open("bug-artifacts/bugs_summary.json") as f:
    summary = json.load(f)

if summary["total_bugs"] == 0:
    → Báo: "🎉 Không có bug nào! Tất cả test pass."
    → DỪNG
```

---

### Step 2: Đọc dữ liệu

**2a. Đọc bugs_summary.json:**
```python
bugs = summary["bugs"]
# Mỗi bug có: tc_id, function, error_message, timestamp, run_id
```

**2b. Đọc test_scenario_map.md (nếu có):**
Map `tc_id` → `{pre_condition_text, steps_text, expected_text, priority, auto_tag, blocked_note, group}`

Format mới của mỗi TC trong `test_scenario_map.md` (8 cột):
```
## TC_GBD.X — [title]
- Pre-condition:
  - Token: TOKEN_*
  - Data: BUNDLE_*
  - DB: ...
- Steps:
  1. Gọi API: Method / URL / Headers / Params hoặc Body
  2. Quan sát response
- Expected Status: NNN
- Response Assertions: ...
- Blocked Note: ...
```

```python
scenario_map = {}
# Parse từng entry trong test_scenario_map.md (format 8 cột):
# ## TC_GBD.3 → pre_condition_text, steps_text, expected_text,
#               expected_status, response_assertions, blocked_note
for tc_id, detail in parse_scenario_map("test_scenario_map.md"):
    scenario_map[tc_id] = detail
```

**2c. Đọc artifact files:**
```python
for bug in bugs:
    tc_id = bug["tc_id"]
    artifact_dir = Path(f"bug-artifacts/{tc_id}")
    bug["has_video"] = (artifact_dir / "video.webm").exists()
    bug["has_screenshot"] = (artifact_dir / "screenshot.png").exists()
    bug["has_trace"] = (artifact_dir / "trace.zip").exists()
```

---

### Step 3: Đánh giá Severity tự động

Logic đánh giá dựa trên error message + TC group:

```python
def auto_severity(error_message: str, tc_group: str, expected_status: int) -> str:
    msg = error_message.lower()

    # Critical: crash, 500, hoặc assert sai hoàn toàn ở happy path
    if "500" in msg or "connection error" in msg or "timeout" in msg:
        return "Critical"
    if tc_group in ["Authentication & Authorization", "Happy Path & Data Integrity"]:
        if "assert" in msg and str(expected_status) in msg:
            return "Critical"

    # Major: sai HTTP status, sai logic nghiệp vụ
    if "assertionerror" in msg and ("status" in msg or "200" in msg or "404" in msg):
        return "Major"
    if tc_group in ["Business Rule", "State Transition", "Data Consistency"]:
        return "Major"

    # Minor: sai field trong response, sai message
    if "assertionerror" in msg and ("data" in msg or "field" in msg):
        return "Minor"

    # Mặc định
    return "Major"
```

---

### Step 4: Parse Actual Result từ error message

Pytest error message thường có dạng:
```
AssertionError: assert 200 == 401
  where 200 = <Response url='https://...' request=<Request url='...'>>
```

Parse thành Actual Result dễ đọc:

```python
def parse_actual_result(error_message: str) -> str:
    """
    Input:  "AssertionError: assert 200 == 401\n  where 200 = <Response...>"
    Output: "API trả về HTTP 200 (expected: 401)"
    """
    import re

    # Pattern: assert A == B
    m = re.search(r"assert (\S+) == (\S+)", error_message)
    if m:
        actual, expected = m.group(1), m.group(2)
        # Nếu là HTTP status
        if actual.isdigit() and int(actual) in [200,201,400,401,403,404,405,429,500]:
            return f"API trả về HTTP {actual} (expected: {expected})"
        # Nếu là field value
        return f"Giá trị thực tế: {actual} (expected: {expected})"

    # Pattern: assert len(...) >= N
    m = re.search(r"assert (\d+) >= (\d+)", error_message)
    if m:
        return f"Response trả về {m.group(1)} item(s) (expected: >= {m.group(2)})"

    # Fallback: lấy dòng đầu tiên
    first_line = error_message.strip().split("\n")[0]
    return first_line[:200]  # Giới hạn 200 ký tự
```

---

### Step 5: Build Summary thành Bug Title

```python
def build_summary(tc_id: str, actual_result: str, module: str) -> str:
    """
    Format chuẩn qc-bug-report: [Module] + mô tả hành vi sai
    """
    # Rút ngắn actual result
    short = actual_result[:80] if len(actual_result) > 80 else actual_result
    return f"[{module}] {tc_id}: {short}"

# Ví dụ:
# "[Bundle Detail] TC_GBD.3: API trả về HTTP 200 (expected: 401)"
# "[Bundle Detail] TC_GBD.12: API trả về HTTP 200 (expected: 400)"
```

---

### Step 6: Sinh Excel — Code Python đầy đủ

```python
import json
import re
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter

# ─── Constants ────────────────────────────────────────────────────────
HEADER_BG   = "1F3864"   # Navy
HEADER_FG   = "FFFFFF"
ROW_BG_ODD  = "FFFFFF"
ROW_BG_EVEN = "F2F2F2"
CRITICAL_BG = "FF0000"
CRITICAL_FG = "FFFFFF"
MAJOR_BG    = "FF6600"
MAJOR_FG    = "FFFFFF"
MINOR_BG    = "FFD966"
MINOR_FG    = "000000"
PARTIAL_BG  = "FFF2CC"
NEW_BG      = "E2EFDA"   # Xanh lá nhạt cho Status=New

HEADERS = [
    "Bug ID", "TC ID", "Module / Endpoint", "Summary",
    "Severity", "Priority", "Steps to Reproduce",
    "Expected Result", "Actual Result", "Attachments",
    "Status", "Note"
]

COL_WIDTHS = [10, 12, 35, 50, 12, 10, 60, 50, 50, 40, 10, 30]

def thin_border():
    s = Side(style="thin")
    return Border(left=s, right=s, top=s, bottom=s)

def make_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def make_align(wrap=True, h="left", v="top"):
    return Alignment(wrap_text=wrap, horizontal=h, vertical=v)

def write_header(ws):
    for col, (header, width) in enumerate(zip(HEADERS, COL_WIDTHS), 1):
        c = ws.cell(row=1, column=col, value=header)
        c.font = Font(name="Arial", size=11, bold=True, color=HEADER_FG)
        c.fill = make_fill(HEADER_BG)
        c.alignment = make_align(h="center", v="center")
        c.border = thin_border()
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[1].height = 25

def write_bug_row(ws, row_num, bug_data: dict, is_even: bool):
    row_bg = ROW_BG_EVEN if is_even else ROW_BG_ODD

    values = [
        bug_data["bug_id"],
        bug_data["tc_id"],
        bug_data["module"],
        bug_data["summary"],
        bug_data["severity"],
        bug_data["priority"],
        bug_data["steps"],
        bug_data["expected"],
        bug_data["actual"],
        bug_data["attachments"],
        "New",
        bug_data.get("note", ""),
    ]

    for col, val in enumerate(values, 1):
        c = ws.cell(row=row_num, column=col, value=val)
        c.font = Font(name="Arial", size=10)
        c.alignment = make_align()
        c.border = thin_border()

        # Màu theo severity (cột E = col 5)
        if col == 5:
            severity = bug_data["severity"]
            if severity == "Critical":
                c.fill = make_fill(CRITICAL_BG)
                c.font = Font(name="Arial", size=10, bold=True, color=CRITICAL_FG)
            elif severity == "Major":
                c.fill = make_fill(MAJOR_BG)
                c.font = Font(name="Arial", size=10, bold=True, color=MAJOR_FG)
            elif severity == "Minor":
                c.fill = make_fill(MINOR_BG)
                c.font = Font(name="Arial", size=10, color=MINOR_FG)
            else:
                c.fill = make_fill(row_bg)
        # Màu PARTIAL (cột L = col 12)
        elif col == 12 and bug_data.get("is_partial"):
            c.fill = make_fill(PARTIAL_BG)
        # Status = New (cột K = col 11)
        elif col == 11:
            c.fill = make_fill(NEW_BG)
            c.alignment = make_align(h="center")
        else:
            c.fill = make_fill(row_bg)

    ws.row_dimensions[row_num].height = 60

def generate_bug_report(
    bugs_summary_path: str = "bug-artifacts/bugs_summary.json",
    scenario_map_path: str = "test_scenario_map.md",
    api_name: str = "API",
    output_dir: str = "/mnt/user-data/outputs",
):
    # ── Đọc dữ liệu ──────────────────────────────────────────────────
    with open(bugs_summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    bugs_raw = summary["bugs"]
    run_date = datetime.now().strftime("%Y%m%d")
    output_path = f"{output_dir}/BugReport_{api_name}_{run_date}.xlsx"

    # ── Build workbook ────────────────────────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = f"Bug Report {run_date}"
    ws.freeze_panes = "A2"  # Freeze header

    write_header(ws)

    for i, bug in enumerate(bugs_raw, 1):
        tc_id     = bug.get("tc_id", "")
        error_msg = bug.get("error_message", "")
        timestamp = bug.get("timestamp", "")

        # Lookup scenario map
        scenario      = scenario_map.get(tc_id, {})
        group         = scenario.get("group", "")
        priority      = scenario.get("priority", "Medium")
        pre_condition = scenario.get("pre_condition_text", "")
        steps_body    = scenario.get("steps_text", "Xem test function tương ứng")
        # Gộp Pre-condition + Steps vào cột "Steps to Reproduce"
        if pre_condition:
            steps = f"Pre-condition:\n{pre_condition}\n\nSteps:\n{steps_body}"
        else:
            steps = steps_body
        expected      = scenario.get("expected_text", "Xem test_scenario_map.md")
        auto_tag      = scenario.get("auto_tag", "FULL")
        blocked       = scenario.get("blocked_note", "")

        # Derive fields
        actual    = parse_actual_result(error_msg)
        severity  = auto_severity(error_msg, group, scenario.get("expected_status", 200))
        summary_  = build_summary(tc_id, actual, api_name)

        # Attachments
        artifact_dir = Path(f"bug-artifacts/{tc_id}")
        attach_parts = []
        if (artifact_dir / "video.webm").exists():
            attach_parts.append(f"video: bug-artifacts/{tc_id}/video.webm")
        if (artifact_dir / "screenshot.png").exists():
            attach_parts.append(f"screenshot: bug-artifacts/{tc_id}/screenshot.png")
        if (artifact_dir / "trace.zip").exists():
            attach_parts.append(f"trace: bug-artifacts/{tc_id}/trace.zip")
        attachments = "\n".join(attach_parts) if attach_parts else "—"

        bug_data = {
            "bug_id":     f"AUTO-{i:03d}",
            "tc_id":      tc_id,
            "module":     api_name,
            "summary":    summary_,
            "severity":   severity,
            "priority":   priority,
            "steps":      steps,
            "expected":   expected,
            "actual":     actual,
            "attachments":attachments,
            "note":       blocked if auto_tag == "PARTIAL" else "",
            "is_partial": auto_tag == "PARTIAL",
        }

        write_bug_row(ws, i + 1, bug_data, is_even=(i % 2 == 0))

    wb.save(output_path)
    return output_path
```

---

### Step 7: In báo cáo tóm tắt + present file

```
✅ Bug Report xuất xong!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TỔNG KẾT TEST RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run ID  : [run_id]
API     : [api_name]
Ngày    : [date]

🐛 Bugs phát hiện: N
  🔴 Critical : n
  🟠 Major    : n
  🟡 Minor    : n
  ⚪ Trivial  : n

📹 Có video  : n bugs
📸 Screenshot: n bugs
⚠️  PARTIAL  : n bugs (cần confirm expected sau khi BA/DEV review)

📁 File: BugReport_<API>_<date>.xlsx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quy tắc quan trọng

- **Bug ID** dùng prefix `AUTO-` để phân biệt với bug manual (`BUG-`)
- **Severity tự đánh giá** — QC review lại trước khi gửi BA/DEV
- **Actual Result** parse từ pytest output — nếu không parse được thì paste nguyên error message (giới hạn 200 ký tự)
- **Attachments**: ghi đường dẫn tương đối, không embed file vào Excel (file lớn)
- **PARTIAL bugs**: cột Note tô vàng, ghi rõ BLOCKED assumption đang dùng
- File Excel **không xóa** `bugs_summary.json` — để có thể re-gen report nếu cần

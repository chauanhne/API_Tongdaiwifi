---
name: write-testcase-ecom
description: >
  Dùng skill này bất cứ khi nào người dùng muốn sinh test case từ tài liệu URD, wireframe, hoặc mô tả nghiệp vụ — đặc biệt cho dự án ECOM hoặc bất kỳ domain thương mại điện tử nào. Trigger khi người dùng đề cập: "viết test case", "sinh test case", "tạo test case", "write test case", "QA", "test scenario", "kiểm thử", "URD", "đặc tả", kèm với file đặc tả hoặc wireframe. Skill này đóng vai trò Senior QA Engineer, phân tích toàn diện tài liệu và xuất ra file Excel (.xlsx) chuẩn. Luôn dùng skill này khi có tài liệu nghiệp vụ + yêu cầu test case, dù người dùng không nói rõ "skill".
---

# Skill: Viết Test Case từ URD + Wireframe

## Vai trò
Bạn là **Senior QA Engineer** chuyên phân tích nghiệp vụ và thiết kế test strategy cho hệ thống ECOM (e-commerce).

---

## Bước 1 — Thu thập Input

Nhận và xử lý các nguồn input sau (có thể kết hợp):

| Nguồn | Cách xử lý |
|---|---|
| File URD (.docx/.pdf) từ Google Drive / Files | Dùng `file-reading` skill để đọc nội dung |
| Hình ảnh Wireframe (upload) | Đọc trực tiếp qua vision — phân tích layout, component, flow |
| Text paste trực tiếp vào chat | Đọc nội dung từ context |

**Nếu có nhiều file / nhiều tính năng trong 1 URD:** Xử lý từng feature riêng biệt, đánh số TC theo feature tương ứng.

---

## Bước 2 — Phân tích tài liệu

Trước khi viết bất kỳ test case nào, **bắt buộc phân tích toàn diện** theo 7 chiều sau:

1. **Input / Output** — Các field nhập liệu, kết quả trả về, API call nếu có
2. **UX/UI** — Layout màn hình, component, trạng thái hiển thị, responsive
3. **Business Rules** — Quy tắc nghiệp vụ, điều kiện, công thức tính toán
4. **User Actions** — Các hành động người dùng có thể thực hiện (click, nhập, chọn, lọc...)
5. **Data Flow** — Luồng dữ liệu từ input → xử lý → output → lưu trữ
6. **Error Handling** — Các trường hợp lỗi, thông báo lỗi, fallback behavior
7. **System Behavior** — Hành vi hệ thống: loading state, timeout, concurrent access

> ⚠️ Nếu thiếu thông tin ở chiều nào → **không suy đoán**, ghi rõ: `"[CẦN BA CONFIRM] Chưa có thông tin trong URD về [nội dung cụ thể]"` và đánh dấu highlight vàng trong Excel.

---

## Bước 3 — Thiết kế Test Cases

### Thứ tự viết test case trong file (KHÔNG phân nhóm, KHÔNG có header/title nhóm — viết liền 1 sheet):

Các test case được viết **liên tục theo thứ tự nhóm** như sau, nhưng **không có dòng tiêu đề nhóm** — phân biệt nhóm bằng **màu nền row** (xem bảng màu bên dưới):

```
1. Permission / Role (nếu có)
2. UI/UX (GUI tổng quan → từng block)
3. Logic / Business Rules
4. Happy Path
5. Negative Cases
6. Boundary Values
7. Edge Cases
8. Validation
9. Input Combinations
10. State Transitions
11. CRUD Operations
12. Error Handling & Messages
13. Performance (nếu có đề cập)
14. Data Consistency (nếu có lưu trữ/đồng bộ)
```

### Bảng màu phân biệt nhóm test case (thay cho tiêu đề nhóm):

| Nhóm | Màu nền row | Hex |
|---|---|---|
| Permission / Role | Tím nhạt | `#E2CFEA` |
| UI/UX | Xanh lá nhạt | `#E2EFDA` |
| Logic / Business Rules | Cam nhạt | `#FCE4D6` |
| Happy Path | Xanh dương nhạt | `#DEEAF1` |
| Negative Cases | Đỏ nhạt | `#FFDCE0` |
| Boundary Values | Vàng nhạt | `#FFF2CC` |
| Edge Cases | Hồng nhạt | `#FCE4EC` |
| Validation | Xanh cyan nhạt | `#DDEBF7` |
| Input Combinations | Xanh ngọc nhạt | `#D9EAD3` |
| State Transitions | Nâu nhạt | `#F4CCCC` |
| CRUD Operations | Xám nhạt | `#F3F3F3` |
| Error Handling | Đỏ đậm hơn | `#F4CCCC` |
| Performance | Xanh đậm nhạt | `#CFE2F3` |
| Data Consistency | Xanh mint nhạt | `#D0E0E3` |

> **Lưu ý quan trọng:** Ưu tiên màu của nhóm **override** màu xen kẽ mặc định. Cells có `[CẦN BA CONFIRM]` vẫn highlight **vàng đậm** (`#FFFF00`) — ưu tiên cao nhất, override tất cả màu nhóm.

### Quy tắc bắt buộc khi viết test case:

**TC ID:**
- Format: `TC_[FeatureIndex].[seq]` — VD: `TC_01.01`, `TC_01.02`, `TC_02.01`
- FeatureIndex là số thứ tự feature (01, 02...) theo URD

**Priority:**
- `High` — core flow, business critical
- `Medium` — luồng phụ, validation quan trọng
- `Low` — UI/cosmetic, non-critical

**Pre-condition:**
- ❌ KHÔNG được chứa bước login hoặc truy cập menu
- ✅ Chỉ ghi điều kiện dữ liệu / trạng thái hệ thống trước khi test
- VD đúng: "Đã có tài khoản user active với role X", "Sản phẩm ID #123 đang ở trạng thái Active"
- VD sai: "User đã login vào hệ thống", "Truy cập vào menu Quản lý sản phẩm"

**Test Title:**
- Bắt đầu bằng động từ **"Check"**
- Rõ ràng, đủ ý, không quá dài
- VD: `Check hiển thị danh sách sản phẩm khi filter theo category`

**Test Steps:**
- Đánh số từ 1, mỗi bước **chỉ 1 action duy nhất**
- Bước nào là action kiểm tra → thêm động từ **"Check"** vào bước đó
- Bước đầu tiên thường là: "Login vào hệ thống với [role]" hoặc "Truy cập vào [màn hình]"
- VD:
  ```
  1. Login vào hệ thống với tài khoản Admin
  2. Truy cập menu "Quản lý sản phẩm"
  3. Nhập keyword "áo" vào ô tìm kiếm
  4. Click button "Tìm kiếm"
  5. Check danh sách kết quả hiển thị
  ```

**Expected Results:**
- Mỗi test case: tối đa **1–3 expected results**
- Mỗi expected result: **1 dòng**, ngắn gọn, rõ ràng
- Chỉ tập trung vào: kết quả cuối cùng (final outcome) + validation quan trọng (error/message/data)
- ❌ Không mô tả lại toàn bộ flow
- ❌ Không chia expected result theo từng bước

### Quy tắc đặc biệt cho Permission:
- Các nhóm quyền **giống nhau** → viết **chung 1 test case**
- Các nhóm quyền **khác nhau** → viết **test case riêng** theo từng nhóm quyền

---

## Bước 4 — Xuất file Excel

Tạo file `.xlsx` với cấu trúc sau:

### Header (Row 1) — Bold, background màu xanh dương đậm, chữ trắng:
| Cột | Tên cột |
|---|---|
| A | Testcase ID |
| B | Mức Độ Ưu Tiên (Priority) |
| C | Nội Dung Test (Test Title) |
| D | Điều Kiện/ Dữ Liệu Test (Pre-condition/ Test Data) |
| E | Các Bước Thực Hiện (Test Steps) |
| F | Kết Quả Mong Đợi (Expected Results) |

### Formatting yêu cầu:
- Font: **Arial 10**
- Header: Bold, fill `#1F4E79` (xanh đậm), font trắng
- **Màu row theo nhóm** (xem bảng màu ở Bước 3 — không dùng xen kẽ trắng/xanh)
- Wrap text cho tất cả cells
- Column width tối ưu: A=14, B=12, C=40, D=35, E=50, F=45
- Border: thin border tất cả cells
- Align: Top cho tất cả cells; Center cho cột A, B
- Cells có nội dung `[CẦN BA CONFIRM]` → highlight **vàng đậm** (`#FFFF00`) — override màu nhóm
- Freeze Row 1 (header)

### Lưu file:
```
/mnt/user-data/outputs/TestCase_[TenFeature]_[YYYYMMDD].xlsx
```

---

## Bước 5 — Trình bày kết quả

Sau khi tạo file Excel:

1. **Tóm tắt phân tích** (inline trong chat) — ngắn gọn:
   - Số features đã phân tích
   - Tổng số test case
   - Phân bổ Priority (High/Medium/Low)
   - Các điểm cần BA confirm (nếu có)

2. **Present file** qua `present_files` tool để user download

---

## Lưu ý kỹ thuật khi tạo Excel

Dùng `openpyxl` để tạo file. Tham khảo xlsx SKILL.md tại `/mnt/skills/public/xlsx/SKILL.md` cho chi tiết kỹ thuật.

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Test Cases"

# Headers
headers = [
    "Testcase ID",
    "Mức Độ Ưu Tiên (Priority)",
    "Nội Dung Test (Test Title)",
    "Điều Kiện/ Dữ Liệu Test (Pre-condition/ Test Data)",
    "Các Bước Thực Hiện (Test Steps)",
    "Kết Quả Mong Đợi (Expected Results)"
]

# Styling
header_fill = PatternFill("solid", fgColor="1F4E79")
header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
warn_fill = PatternFill("solid", fgColor="FFFF00")  # BA confirm — override all
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
col_widths = [14, 12, 40, 35, 50, 45]

# Màu nhóm — áp dụng cho toàn bộ row theo nhóm
GROUP_COLORS = {
    "permission":    "E2CFEA",
    "uiux":          "E2EFDA",
    "logic":         "FCE4D6",
    "happy_path":    "DEEAF1",
    "negative":      "FFDCE0",
    "boundary":      "FFF2CC",
    "edge":          "FCE4EC",
    "validation":    "DDEBF7",
    "combination":   "D9EAD3",
    "state":         "F4CCCC",
    "crud":          "F3F3F3",
    "error":         "F4CCCC",
    "performance":   "CFE2F3",
    "consistency":   "D0E0E3",
}

# Khi tô màu row, dùng:
# fill = PatternFill("solid", fgColor=GROUP_COLORS["happy_path"])
# for cell in row: cell.fill = fill
# Nếu cell chứa "[CẦN BA CONFIRM]": cell.fill = warn_fill (override)
```

**Khi viết Test Steps vào cell** — dùng newline `\n` để ngăn cách các bước:
```python
steps_text = "1. Login vào hệ thống với tài khoản Admin\n2. Truy cập menu...\n3. Check..."
cell.alignment = Alignment(wrap_text=True, vertical="top")
```

---

## Checklist trước khi xuất file

- [ ] Tất cả TC ID đúng format `TC_XX.YY`
- [ ] Không có Pre-condition chứa bước login/truy cập menu
- [ ] Tất cả Test Title bắt đầu bằng "Check"
- [ ] Mỗi Expected Result ≤ 3 dòng, mỗi dòng ≤ 1 ý
- [ ] Các thông tin thiếu đã được ghi rõ `[CẦN BA CONFIRM]` và highlight vàng
- [ ] File đã được lưu vào `/mnt/user-data/outputs/`
- [ ] Đã gọi `present_files` để user có thể download

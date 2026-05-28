---
name: write-urd-ecom
description: >
  Dùng skill này bất cứ khi nào người dùng muốn tổng hợp, viết lại, hoặc tạo mới tài liệu URD (User Requirement Document) từ các file URD có sẵn hoặc wireframe — đặc biệt cho dự án ECOM. Trigger khi người dùng đề cập: "viết URD", "tạo URD", "tổng hợp URD", "write URD", "gộp URD", "viết lại URD", "tài liệu đặc tả", "đặc tả nghiệp vụ", "BA document", "business requirement", kèm theo file URD (.docx/.pdf) hoặc wireframe. Skill này đóng vai trò Senior Business Analyst, phân tích toàn diện tài liệu và xuất ra file URD hoàn chỉnh định dạng .docx. Luôn dùng skill này khi có file URD hoặc wireframe + yêu cầu tổng hợp / viết lại tài liệu nghiệp vụ, dù người dùng không nói rõ "skill".
---

# Skill: Viết / Tổng hợp URD từ Files + Wireframe

## Vai trò
Bạn là **Senior Business Analyst** chuyên phân tích nghiệp vụ và thiết kế flow cho hệ thống ECOM (e-commerce platform — ECP).

---

## Bước 1 — Thu thập Input

Nhận và xử lý theo thứ tự ưu tiên sau. Kiểm tra từng nguồn và dùng cách phù hợp nhất:

| Ưu tiên | Nguồn Input | Cách xử lý |
|---|---|---|
| 1 | **File .docx/.pdf upload trực tiếp vào chat** | Dùng `file-reading` skill + `pdf-reading` skill — **luôn hoạt động, ưu tiên cao nhất** |
| 2 | **Google Docs native link** (tạo bằng Google Docs, không phải .docx upload) | Dùng `google_drive_fetch` tool với Document ID |
| 3 | **File .docx/.pdf upload lên Google Drive** | ❌ Không đọc được tự động — yêu cầu user tải về máy rồi upload vào chat |
| 4 | **Hình ảnh Wireframe** (upload) | Đọc qua vision — phân tích layout, component, field |
| 5 | **Link Figma** | Ghi nhận URL, mention trong mục 5.1 Thiết kế |
| 6 | **Text paste** trực tiếp | Đọc từ context |

> ⚠️ Nếu có **nhiều file** → đọc toàn bộ, gộp tất cả chức năng, không bỏ sót file nào.
>
> ⚠️ **Phân biệt quan trọng:** File `.docx` **upload lên** Google Drive ≠ Google Docs native. `google_drive_fetch` chỉ đọc được Google Docs tạo trực tiếp trong Google Docs (mime type: `application/vnd.google-apps.document`). Nếu mime type là `application/vnd.openxmlformats-officedocument.wordprocessingml.document` → phải yêu cầu user tải về và upload thẳng vào chat.

---

### 1.1 Xử lý link Google Drive / Google Docs

#### BƯỚC ĐẦU TIÊN — Dùng `google_drive_fetch` tool (ưu tiên cao nhất)

Tool `google_drive_fetch` có thể đọc trực tiếp **Google Docs** bằng Document ID — không cần login, không cần quyền public.

**Cách trích xuất Document ID từ URL:**

```
https://docs.google.com/document/d/[DOCUMENT_ID]/edit
https://docs.google.com/document/d/[DOCUMENT_ID]/view
https://drive.google.com/file/d/[FILE_ID]/view
```

**Cách gọi tool:**
```
google_drive_fetch(document_ids=["DOCUMENT_ID_1", "DOCUMENT_ID_2"])
```

Có thể truyền nhiều ID cùng lúc để đọc nhiều file song song.

> ✅ Đây là cách ưu tiên nhất. Thử `google_drive_fetch` trước khi dùng bất kỳ cách nào khác.

---

#### BƯỚC DỰ PHÒNG — Nếu `google_drive_fetch` không khả dụng hoặc lỗi

**Trường hợp B1 — Link Google Docs (gdoc native)**

URL dạng: `https://docs.google.com/document/d/FILE_ID/edit`

Chuyển sang export URL rồi dùng `web_fetch`:

| Mục đích | Export URL |
|---|---|
| Đọc text thuần | `https://docs.google.com/document/d/FILE_ID/export?format=txt` |
| Tải về dạng .docx | `https://docs.google.com/document/d/FILE_ID/export?format=docx` |

```
web_fetch("https://docs.google.com/document/d/FILE_ID/export?format=txt")
```

**Trường hợp B2 — Link Google Drive (file .docx / .pdf đã upload)**

URL dạng: `https://drive.google.com/file/d/FILE_ID/view`

```
web_fetch("https://drive.google.com/uc?export=download&id=FILE_ID")
```

Nếu kết quả là binary (.docx):
1. Lưu xuống `/home/claude/urd_temp.docx`
2. Dùng `file-reading` skill để đọc tiếp

**Trường hợp B3 — Dùng `google_drive_search` tìm file theo tên**

Nếu user không có link nhưng biết tên file:
```
google_drive_search(query="tên file URD")
→ Lấy document_id từ kết quả
→ Gọi google_drive_fetch(document_id)
```

---

#### LƯU Ý QUAN TRỌNG — File .docx trên Google Drive

Khi file được **upload lên Google Drive dưới dạng .docx** (không phải Google Docs native), tất cả các phương pháp tự động đều bị giới hạn:

| Phương pháp | Kết quả với .docx |
|---|---|
| `google_drive_fetch` | ❌ Chỉ đọc được Google Docs native |
| `web_fetch` export URL | ❌ Claude không tự tạo drive.google.com URL |
| Link gốc .docx | ❌ Cần xác thực Google |

**Giải pháp — hướng dẫn user làm 1 trong 2:**

> **Cách 1 (nhanh nhất):** Tải file .docx về máy → Upload trực tiếp vào chat bằng icon 📎
>
> **Cách 2:** Mở file trong Google Drive → Chọn "Mở bằng Google Docs" → File tự chuyển sang Google Docs native → Copy link mới → Paste vào chat → Dùng `google_drive_fetch` đọc bình thường

---

#### XỬ LÝ LỖI khi đọc Google Drive

| Lỗi | Nguyên nhân | Xử lý |
|---|---|---|
| 403 Forbidden | File chưa share công khai | Yêu cầu user share "Anyone with the link can view" hoặc upload trực tiếp |
| 401 Unauthorized | Chưa đăng nhập | Gợi ý kết nối Google Drive qua Tools (🔌) |
| File binary không đọc được | .docx raw binary | Lưu file → dùng `file-reading` skill |
| Nội dung trống | Link sai hoặc file bị xóa | Thông báo user kiểm tra lại link |

---

#### GỢI Ý KẾT NỐI Google Drive MCP (nếu chưa kết nối)

Nếu không dùng được `google_drive_fetch` và `web_fetch` đều lỗi 401/403, thông báo:

> "Tôi không thể truy cập file Google Drive này. Để đọc file private của bạn, có 3 cách:
> 1. **Kết nối Google Drive** qua mục Tools (🔌) trong Claude để tôi truy cập trực tiếp
> 2. **Chia sẻ link** với quyền 'Anyone with the link can view'
> 3. **Tải file** về máy và upload trực tiếp vào chat"

---

## Bước 2 — Phân tích tài liệu

Trước khi viết URD, **bắt buộc phân tích toàn diện** theo 7 chiều:

1. **Input / Output** — Các trường nhập liệu, kết quả trả về, API call nếu có
2. **UX/UI** — Layout màn hình, component, trạng thái hiển thị
3. **Business Rules** — Quy tắc nghiệp vụ, điều kiện, công thức tính toán
4. **User Actions** — Hành động người dùng: click, nhập, chọn, lọc, tìm kiếm...
5. **Data Flow** — Luồng dữ liệu từ input → xử lý → output → lưu trữ
6. **Error Handling** — Các trường hợp lỗi, thông báo lỗi, fallback
7. **System Behavior** — Hành vi hệ thống: loading state, timeout, phân quyền

> ⚠️ Nếu thiếu thông tin → **không tự suy đoán**. Ghi rõ: `"[CẦN BA/PO CONFIRM] Chưa có thông tin trong URD về [nội dung cụ thể]"` và highlight trong tài liệu.

---

## Bước 3 — Cấu trúc file URD Output

File URD được xuất dạng `.docx`. Mỗi chức năng có cấu trúc như sau:

---

### 3.1 Tên chức năng

- Đánh số thứ tự: `1.`, `2.`, `3.` — **In đậm**
- Ví dụ: **1. Tạo mới gói bán**, **2. Chỉnh sửa gói bán**
- Sắp xếp theo thứ tự logic nghiệp vụ (từ tổng quan → chi tiết)

---

### 3.2 Thông tin chung

Heading con đánh số: `1.1`, `2.1`, `3.1` tương ứng theo chức năng — **In đậm**

---

### 3.3 Bảng Use Case (2 cột)

Tạo bảng 2 cột cho mỗi chức năng:

| Tên chức năng | Nội dung |
|---|---|
| Actor | [Vai trò người dùng: Admin, Seller, System...] |
| Mô tả Use Case | [Mô tả ngắn gọn chức năng này làm gì] |
| Trigger (Kích hoạt) | [Điều kiện nào khởi động chức năng này] |
| Priority | [High / Medium / Low] |
| Pre-condition (Điều kiện tiên quyết) | [Điều kiện phải đúng trước khi thực hiện] |
| Post-condition (Kết quả sau khi thực hiện) | [Kết quả cuối khi chức năng hoàn thành] |
| Basic Flow (Luồng chính) | [Liệt kê bước 1, 2, 3... — happy path] |
| Alternative Flow (Luồng thay thế) | [Luồng khác có thể xảy ra, không phải lỗi] |
| Exception Flow (Luồng ngoại lệ) | [Khi có lỗi, validation fail, exception...] |
| Business Rules (Quy tắc nghiệp vụ) | [Các rule cứng từ URD — KHÔNG tự suy đoán] |

> **Business Rules**: Chỉ viết rule đã có trong file URD gốc. Nếu thiếu rule → ghi `[CẦN BA/PO CONFIRM]`.

---

### 3.4 Luồng nghiệp vụ

**3.4.1 Sơ đồ luồng (User Story)**

Mô tả luồng từ User → Hệ thống ECP theo dạng text có mũi tên:
```
Người dùng → [Hành động] → Hệ thống ECP → [Phản hồi] → Người dùng
```

**3.4.2 Bảng mô tả luồng (3 cột)**

| Bước | Actor | Mô tả |
|---|---|---|
| 1 | Người dùng | [Hành động của user] |
| 2 | Hệ thống | [Phản hồi/xử lý của ECP] |
| 3 | Người dùng | [Tiếp tục hành động] |
| ... | ... | ... |

- Cột **Bước**: số thứ tự tăng dần từ 1
- Cột **Actor**: `Người dùng` hoặc `Hệ thống`
- Cột **Mô tả**: Mô tả rõ hành động/phản hồi

---

### 3.5 Giao diện

**5.1 Thiết kế**

> Hình ảnh wireframe của màn hình/chức năng.  
> Link Figma: [URL được cung cấp bởi người dùng]

Nếu có wireframe image → chèn vào đây.  
Nếu chỉ có link Figma → ghi link và ghi chú "Xem thiết kế tại Figma".

**5.2 Mô tả trường dữ liệu (6 cột)**

Tạo bảng 6 cột liệt kê **đầy đủ** tất cả trường có trên wireframe:

| STT | Tên trường | Kiểu dữ liệu | Bắt buộc | Giá trị khởi tạo | Mô tả |
|---|---|---|---|---|---|
| 1 | [Tên trường] | [Label/Dropdown/Textbox/Button/Text/DateTime/Component/Icon/Image/...] | Y/N | [Giá trị default hoặc N/A] | [Mô tả rule, liệt kê giá trị nếu Dropdown] |

**Quy tắc bắt buộc cho bảng trường dữ liệu:**

- **Thứ tự liệt kê**: từ trên xuống → từ trái qua phải → từ ngoài vào trong theo wireframe
- **Trường trùng tên nhưng khác block**: vẫn phải liệt kê riêng, ghi rõ block
- **Kiểu dữ liệu**: Label, Dropdown, Textbox, Button, Text, DateTime, Component, Icon, Image, Checkbox, Radio, Toggle, Tab, Badge, Tooltip
- **Bắt buộc**: `Y` = có validation required; `N` = optional
- **Giá trị khởi tạo**: giá trị default ban đầu khi mở màn hình. Nếu không có → `N/A`
- **Mô tả**: rule chi tiết + liệt kê tất cả giá trị nếu là Dropdown
- Nếu trường không có mô tả trong URD → ghi `[CẦN BA/PO CONFIRM]` ở cột Mô tả

---

## Bước 4 — Quy tắc viết tài liệu

### Nguyên tắc chung:
- Tất cả **đầu mục chức năng** phải **in đậm**
- Business Rules chỉ dựa trên URD gốc — không tự suy đoán
- Phần nào thiếu thông tin → highlight và ghi `[CẦN BA/PO CONFIRM]`
- Liệt kê **đầy đủ** tất cả trường, không bỏ sót dù trường đơn giản
- Thứ tự: trên → dưới, trái → phải, ngoài → trong (theo wireframe)

### Cấu trúc heading trong file .docx:
```
Heading 1 → Tên chức năng (VD: 1. Tạo mới gói bán)
Heading 2 → Thông tin chung (VD: 1.1 Thông tin chung)
Heading 2 → Luồng nghiệp vụ (VD: 1.2 Luồng nghiệp vụ)
Heading 2 → Giao diện (VD: 1.3 Giao diện)
Heading 3 → 5.1 Thiết kế / 5.2 Mô tả trường dữ liệu
```

---

## Bước 5 — Tạo file .docx

Dùng `docx` npm package (JavaScript). Tham khảo SKILL.md tại `/mnt/skills/public/docx/SKILL.md`.

### Cài đặt:
```bash
npm install -g docx
```

### Template cơ bản:

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        VerticalAlign } = require('docx');
const fs = require('fs');

// Màu header bảng
const TABLE_HEADER_COLOR = "1F4E79"; // xanh đậm
const TABLE_HEADER_FONT_COLOR = "FFFFFF";
const CONFIRM_HIGHLIGHT = "FFFF00"; // vàng — [CẦN BA/PO CONFIRM]

// Border chuẩn cho bảng
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

// Hàm tạo cell header bảng Use Case (cột trái)
function makeHeaderCell(text, width = 2500) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: TABLE_HEADER_COLOR, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, color: TABLE_HEADER_FONT_COLOR, font: "Arial", size: 20 })]
    })]
  });
}

// Hàm tạo cell nội dung
function makeContentCell(text, width = 6860, highlight = false) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: highlight ? { fill: CONFIRM_HIGHLIGHT, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, font: "Arial", size: 20 })]
    })]
  });
}

// Hàm tạo 1 row của bảng Use Case
function makeUseCaseRow(label, content) {
  const hasConfirm = content.includes("[CẦN BA/PO CONFIRM]");
  return new TableRow({
    children: [
      makeHeaderCell(label, 2500),
      makeContentCell(content, 6860, hasConfirm)
    ]
  });
}

// Hàm tạo bảng Use Case cho 1 chức năng
function makeUseCaseTable(data) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2500, 6860],
    rows: [
      makeUseCaseRow("Actor", data.actor),
      makeUseCaseRow("Mô tả Use Case", data.moTaUseCase),
      makeUseCaseRow("Trigger (Kích hoạt)", data.trigger),
      makeUseCaseRow("Priority", data.priority),
      makeUseCaseRow("Pre-condition (Điều kiện tiên quyết)", data.preCondition),
      makeUseCaseRow("Post-condition (Kết quả sau khi thực hiện)", data.postCondition),
      makeUseCaseRow("Basic Flow (Luồng chính)", data.basicFlow),
      makeUseCaseRow("Alternative Flow (Luồng thay thế)", data.alternativeFlow),
      makeUseCaseRow("Exception Flow (Luồng ngoại lệ)", data.exceptionFlow),
      makeUseCaseRow("Business Rules (Quy tắc nghiệp vụ)", data.businessRules),
    ]
  });
}

// Hàm tạo bảng Luồng nghiệp vụ
function makeFlowTable(steps) {
  const headerRow = new TableRow({
    children: [
      makeHeaderCell("Bước", 1200),
      makeHeaderCell("Actor", 2000),
      makeHeaderCell("Mô tả", 6160),
    ]
  });
  const dataRows = steps.map(step => new TableRow({
    children: [
      new TableCell({ borders, width: { size: 1200, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: String(step.buoc), font: "Arial", size: 20 })] })] }),
      new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: step.actor, font: "Arial", size: 20 })] })] }),
      new TableCell({ borders, width: { size: 6160, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: step.moTa, font: "Arial", size: 20 })] })] }),
    ]
  }));
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1200, 2000, 6160],
    rows: [headerRow, ...dataRows]
  });
}

// Hàm tạo bảng Mô tả trường dữ liệu (6 cột)
function makeFieldTable(fields) {
  const colWidths = [600, 2000, 1500, 900, 1500, 2860]; // tổng ~9360
  const headers = ["STT", "Tên trường", "Kiểu dữ liệu", "Bắt buộc", "Giá trị khởi tạo", "Mô tả"];
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: TABLE_HEADER_COLOR, type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 80, right: 80 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: h, bold: true, color: TABLE_HEADER_FONT_COLOR, font: "Arial", size: 18 })] })]
    }))
  });
  const dataRows = fields.map((f, idx) => {
    const hasConfirm = (f.moTa || "").includes("[CẦN BA/PO CONFIRM]");
    return new TableRow({
      children: [
        new TableCell({ borders, width: { size: colWidths[0], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: String(idx + 1), font: "Arial", size: 18 })] })] }),
        new TableCell({ borders, width: { size: colWidths[1], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ children: [new TextRun({ text: f.tenTruong, font: "Arial", size: 18 })] })] }),
        new TableCell({ borders, width: { size: colWidths[2], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ children: [new TextRun({ text: f.kieuDuLieu, font: "Arial", size: 18 })] })] }),
        new TableCell({ borders, width: { size: colWidths[3], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: f.batBuoc, font: "Arial", size: 18 })] })] }),
        new TableCell({ borders, width: { size: colWidths[4], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ children: [new TextRun({ text: f.giaTriKhoiTao, font: "Arial", size: 18 })] })] }),
        new TableCell({ borders, width: { size: colWidths[5], type: WidthType.DXA },
          shading: hasConfirm ? { fill: CONFIRM_HIGHLIGHT, type: ShadingType.CLEAR } : undefined,
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ children: [new TextRun({ text: f.moTa, font: "Arial", size: 18 })] })] }),
      ]
    });
  });
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows]
  });
}
```

### Lưu file:
```bash
# Lưu vào output
/mnt/user-data/outputs/URD_[TenDuAn]_[YYYYMMDD].docx
```

---

## Bước 6 — Trình bày kết quả

Sau khi tạo file .docx:

1. **Tóm tắt** ngắn trong chat:
   - Số chức năng đã tổng hợp
   - Danh sách tên chức năng
   - Số trường dữ liệu trong bảng mô tả
   - Các mục `[CẦN BA/PO CONFIRM]` nếu có

2. **Present file** qua `present_files` tool để user download

---

## Checklist trước khi xuất file

- [ ] Đã đọc toàn bộ file URD input
- [ ] Tất cả chức năng được đánh số và **in đậm**
- [ ] Bảng Use Case đủ 10 hàng cho mỗi chức năng
- [ ] Luồng nghiệp vụ có cả sơ đồ text + bảng 3 cột
- [ ] Bảng mô tả trường: đủ 6 cột, đúng thứ tự wireframe
- [ ] Không có Business Rule tự suy đoán — chỉ từ URD gốc
- [ ] Trường thiếu thông tin đã ghi `[CẦN BA/PO CONFIRM]`
- [ ] File đã validate thành công
- [ ] File lưu tại `/mnt/user-data/outputs/`
- [ ] Đã gọi `present_files`

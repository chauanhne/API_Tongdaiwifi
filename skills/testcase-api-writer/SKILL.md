---
name: testcase-api-writer
description: >
  Sinh test case kiểm thử API REST từ API spec (endpoint, method, request/response schema,
  error codes, business rule). Nhận đầu vào dạng: text/swagger/postman, file .docx upload,
  hoặc link Google Sheet/Google Docs. Xuất ra file .xlsx đúng chuẩn 9 cột của dự án, kèm
  báo cáo tóm tắt ASSUMPTION và rule còn thiếu. Dùng skill này bất cứ khi nào user yêu cầu:
  viết testcase API, sinh TC cho API, test API endpoint, generate test case REST API,
  kiểm thử API, hoặc nhắc đến endpoint/swagger/postman/google sheet/docx cần kiểm thử —
  dù họ có upload file spec hay chưa. Skill cover đầy đủ: auth, validate, boundary,
  business rule, happy path, state transition, idempotency, error handling,
  performance, data consistency, network/timeout.
---

# Testcase API Writer

> ⚠️ **BẮT BUỘC**: Đọc `/mnt/skills/user/testcase-base/SKILL.md` TRƯỚC khi làm bất cứ gì.
> Skill này chỉ định nghĩa **luồng xử lý đặc thù cho API** — toàn bộ chuẩn format,
> quy tắc viết, checklist chất lượng, và code Python lấy từ **testcase-base**.

---

## Bước 0 — Thu thập đầu vào

| Đầu vào | Bắt buộc? | Dạng hỗ trợ | Mục đích |
|---------|-----------|-------------|----------|
| API Spec | Bắt buộc | text, swagger/openapi YAML/JSON, Postman collection, file `.docx`, link Google Sheet / Google Docs | Endpoint, method, request schema, response schema, error codes |
| Business Rule / tài liệu nghiệp vụ | Nên có | text, `.docx`, link Google Sheet / Google Docs | Điều kiện validate, flow nghiệp vụ |
| File testcase mẫu (.xlsx) | Nên có | `.xlsx` upload | Format, style chuẩn dự án |
| Tên API / Function ID | Bắt buộc | text | Đặt tên TC, nhóm scope |

> Thiếu spec API hoặc tên chức năng → **hỏi user trước** khi tiếp tục.

---

## Bước 0.5 — Đọc file đầu vào

Trước khi phân tích, xác định dạng đầu vào và đọc theo hướng dẫn tương ứng:

### A. File .docx (upload)

```
1. Đọc /mnt/skills/public/docx/SKILL.md để biết cách extract text
2. Dùng extract-text /mnt/user-data/uploads/<filename>.docx
3. Parse nội dung: tìm các section có từ khóa endpoint, method, request, response,
   error code, business rule, validate
4. Nếu file có nhiều API → hỏi user muốn gen TC cho API nào trước
```

### B. Link Google Sheet

```
1. Nhận URL dạng: https://docs.google.com/spreadsheets/d/<id>/...
2. Dùng tool google_drive_fetch với document_id = <id> trích xuất từ URL
3. Parse dữ liệu dạng bảng: mỗi row thường là 1 endpoint hoặc 1 field
4. Mapping cột → các trường: method, url, param name, type, required, description,
   error code, response example
5. Nếu sheet có nhiều tab → đọc tất cả tab, tổng hợp thành 1 spec hoàn chỉnh
```

### C. Link Google Docs

```
1. Nhận URL dạng: https://docs.google.com/document/d/<id>/...
2. Dùng tool google_drive_fetch với document_id = <id>
3. Parse nội dung văn bản: tìm heading chứa tên API/endpoint,
   các bảng mô tả request/response, danh sách error code
4. Xử lý tương tự như .docx sau khi đã có plain text
```

### D. Text / Swagger / Postman (paste trực tiếp)

```
Không cần bước đọc file — parse trực tiếp từ nội dung user cung cấp trong chat.
```

> ⚠️ Sau khi đọc file xong, **in tóm tắt ngắn** ra chat để user xác nhận trước khi viết TC:
> - Số endpoint tìm được
> - Danh sách method + URL
> - Số required field / error code đọc được
> - Những phần không rõ → liệt kê vào [CẦN CONFIRM BA/DEV]

---

## Bước 1 — Phân tích API Spec

### 1.1 Trích xuất thông tin cần thiết

Từ spec đầu vào, trích xuất đầy đủ:

**A. Thông tin endpoint**
| Field | Giá trị |
|-------|---------|
| Method | GET / POST / PUT / PATCH / DELETE |
| URL | /api/v1/... |
| Authentication | Bearer Token / API Key / None |
| Content-Type | application/json / multipart / ... |

**B. Request Parameters**
| Tên field | Kiểu | Bắt buộc | Ràng buộc (min/max, format, enum) |
|-----------|------|----------|-----------------------------------|
| ...       | ...  | Y/N      | ...                               |

**C. Response Schema (Success)**
- HTTP Status: 200 / 201 / ...
- Từng field trong response body + kiểu dữ liệu

**D. Error Codes**
| HTTP Code | Error Code | Message | Trigger khi nào |
|-----------|-----------|---------|-----------------|
| 400 | ... | ... | ... |
| 401 | ... | ... | ... |

**E. Business Rules (BR01, BR02…)**

**F. [ASSUMPTION]** — spec chưa nói rõ, phải giả định

**G. [CẦN CONFIRM BA/DEV]** — rule còn thiếu hoặc mâu thuẫn

---

## Bước 2 — Lập Test Data Catalog

Trước khi viết TC, lập bảng test data cho toàn bộ API. Áp dụng nguyên tắc isolation từ **testcase-base mục 4**.

### Naming Convention đặc thù API

| Pattern | Ví dụ | Dùng khi |
|---------|-------|----------|
| `{Obj}_VALID_{N}` | USER_VALID_001 | Happy path — request hợp lệ |
| `{Obj}_AUTH_{ROLE}` | USER_AUTH_ADMIN | TC phân quyền theo role |
| `{Obj}_VALIDATE_NULL_{FIELD}` | USER_VALIDATE_NULL_EMAIL | TC bỏ trống từng field |
| `{Obj}_VALIDATE_FMT_{FIELD}` | USER_VALIDATE_FMT_PHONE | TC sai format field |
| `{Obj}_BOUND_{FIELD}_{MIN/MAX}` | USER_BOUND_NAME_MAX | TC boundary từng field |
| `{Obj}_DUP_{N}` | USER_DUP_001 | TC idempotency / duplicate |
| `{Obj}_STATE_{TRANG_THAI}` | ORDER_STATE_CANCELLED | TC state transition |
| `{Obj}_NET_{N}` | USER_NET_001 | TC network/timeout |
| `{Obj}_PERF_{N}` | USER_PERF_001 | TC performance / rate limit |
| `TOKEN_{ROLE}_{STATUS}` | TOKEN_ADMIN_VALID | Token theo role và trạng thái |
| `TOKEN_{STATUS}` | TOKEN_EXPIRED, TOKEN_INVALID | Token lỗi |

> ⚠️ TC idempotency, network, performance phải dùng object RIÊNG — không share với happy path.

---

## Bước 3 — Viết Test Case

Áp dụng toàn bộ quy tắc từ **testcase-base**, cộng với quy tắc bổ sung API bên dưới.

### Thứ tự Group chuẩn cho API

```
Authentication & Authorization      ← LUÔN ĐẦU TIÊN
Validate — Required Fields
Validate — Format / Type
Validate — Boundary Values
Business Rule
Happy Path & Data Integrity
State Transition
Idempotency / Duplicate Request
Error Handling
Performance / Rate Limit
Data Consistency
Network / Timeout
```

---

## Quy tắc API-specific (bắt buộc)

### A1 — Cột E "Pre-condition / Test Data" phải liệt kê đủ token, data object, trạng thái DB

```
- Token: TOKEN_ADMIN_VALID (Bearer token hợp lệ, còn hạn, đủ quyền)
- Data: BUNDLE_VALID_001 (status=ACTIVE, có ≥1 dòng giá active+approved)
- DB: bảng bundle có record bundleId=BUNDLE_VALID_001
```

❌ Sai: `Dữ liệu hợp lệ`
✅ Đúng: liệt kê từng object theo naming convention, kèm điều kiện DB nếu cần

---

### A1b — Cột F "Các Bước Thực Hiện" phải ghi đủ: bước số + Method + URL + Headers + Body/Params

**POST / PUT / PATCH:**
```
1. Gọi API:
   Method: POST
   URL: /api/v1/users
   Headers: { "Authorization": "Bearer TOKEN_ADMIN_VALID", "Content-Type": "application/json" }
   Body: { "name": "Nguyen Van A", "email": "test@example.com", "role": "USER" }
2. Quan sát response trả về
```

**GET / DELETE:**
```
1. Gọi API:
   Method: GET
   URL: /api/v1/bundles/{BUNDLE_VALID_001}
   Headers: { "Authorization": "Bearer TOKEN_ADMIN_VALID" }
   Params: { "channelCode": "FPT_WEB", "customerType": "KH_MOI" }
2. Quan sát response trả về
```

❌ Sai: `Gọi API tạo user với dữ liệu hợp lệ`
✅ Đúng: ghi rõ từng bước có đánh số, Method, URL, Headers, Body/Params với giá trị data object cụ thể

---

### A2 — Expected Result phải có đủ 3 lớp assertion

```
- HTTP Status: 201
- response.data.id không null (auto-generated)
- response.data.email = 'test@example.com'
- response.data.status = 'active'
- response.data.role = 'USER'
- DB: bảng users ghi nhận email='test@example.com', created_at không null
```

❌ Sai: `- API trả về 201 và tạo user thành công`
✅ Đúng: assert HTTP status + từng field response + side effect DB nếu có

---

### A3 — TC Authentication phải cover đủ 5 case

Bắt buộc có TC cho từng case:
1. Token hợp lệ → 200/201 (happy path auth)
2. Không có token (thiếu header Authorization) → 401
3. Token sai / giả mạo → 401
4. Token hết hạn → 401
5. Token đúng nhưng không đủ quyền (sai role) → 403

---

### A4 — TC Validate phải cover từng field bắt buộc RIÊNG LẺ

Với mỗi field bắt buộc, tạo ít nhất 2 TC:
- Bỏ trống field đó (null/empty) → assert error code + message cụ thể
- Sai format/type → assert error code + message cụ thể

❌ Sai: 1 TC bỏ trống tất cả field cùng lúc
✅ Đúng: mỗi field 1 TC riêng → xác định đúng validation per-field

---

### A5 — TC Idempotency phải ghi rõ interval

```
Steps:
  1. Gọi POST /api/v1/orders với body ORDER_DUP_001 (lần 1)
  2. Trong vòng < 500ms, gọi lại cùng request (lần 2)
  3. Quan sát response lần 2 và trạng thái DB

Expected:
  - Lần 1: HTTP 201, order tạo thành công
  - Lần 2: HTTP 200 (idempotent) HOẶC HTTP 409 (conflict) — [BLOCKED confirm behavior]
  - DB: chỉ có 1 bản ghi order, không tạo duplicate
```

---

### A6 — TC Network/Timeout phải chỉ rõ cách simulate

```
Steps:
  1. Bắt đầu gọi POST /api/v1/... với body hợp lệ
  2. Ngay khi request đang in-flight (sau khi gửi, trước khi nhận response):
     simulate network drop (dùng Charles Proxy / Wireshark / tc netem)
  3. Quan sát behavior của client và trạng thái DB

Expected:
  - Client nhận connection error (không phải 2xx)
  - DB: KHÔNG có bản ghi mới (rollback thành công)
     HOẶC nếu đã commit: idempotency key đảm bảo không duplicate khi retry
```

---

### A7 — TC Performance phải ghi rõ concurrency và threshold

```
Pre-condition: X concurrent requests chuẩn bị sẵn với USER_PERF_001...USER_PERF_X

Steps:
  1. Gửi đồng thời X requests GET /api/v1/users trong vòng 1 giây
  2. Quan sát response time và HTTP status

Expected:
  - Tất cả X requests trả về HTTP 200
  - Response time ≤ [Y]ms cho 95th percentile
  HOẶC nếu vượt rate limit:
  - Request thứ [N+1] trở đi trả về HTTP 429 với message 'Too Many Requests'
```

---

## Bước 4 — Tạo file Excel

Đọc skill xlsx trước:
```
/mnt/skills/public/xlsx/SKILL.md
```

Dùng code Python từ **testcase-base mục 6** để xuất file .xlsx.

Tên file: `AI_ClaudeCode_API_<TênEndpoint>.xlsx`

### Cấu trúc cột file TC (8 cột)

| Cột | Tên cột | Nội dung |
|-----|---------|----------|
| A | QC/AI | `AI` hoặc `QC` |
| B | Testcase ID | `TC_<API_CODE>.<số>` (ví dụ: TC_API.1) |
| C | Priority | `High` / `Medium` / `Low` |
| D | Nội Dung Test (Test Title) | Tên TC, bắt đầu bằng "Check" |
| E | Pre-condition / Test Data | Token dùng, data object, trạng thái DB cần có trước khi test |
| F | Các Bước Thực Hiện | Các bước thực hiện: Method, URL, Headers, Body/Params với giá trị cụ thể |
| G | Kết Quả Mong Đợi (Expected Result) | HTTP status + response assertions + DB side effect |
| H | Khả Năng Auto | `✅ Auto được` / `⚠️ Auto được một phần` / `❌ Khó auto` |

---

## Bước 5 — Output cuối cùng

### 5.1 File .xlsx
- Lưu vào `/mnt/user-data/outputs/AI_ClaudeCode_API_<TênEndpoint>.xlsx`
- Gọi `present_files` để trả về user

### 5.2 Báo cáo tóm tắt
In ra chat:

```markdown
## 📋 BÁO CÁO TÓM TẮT — API Test Case

### Endpoint
[METHOD] /api/v1/...

### Tổng số Testcase & Phân bổ
| Group | Số TC | High | Medium | Low |
|-------|-------|------|--------|-----|
| Authentication & Authorization | X | X | X | X |
| Validate — Required Fields | X | X | X | X |
| ... | ... | ... | ... | ... |
| **TỔNG** | **N** | **X** | **X** | **X** |

### Đánh giá Khả Năng Auto
| Mức độ | Số TC | % |
|--------|-------|---|
| ✅ Auto được | X | X% |
| ⚠️ Auto được một phần | X | X% |
| ❌ Khó auto | X | X% |

### [ASSUMPTION]
- ...

### [CẦN CONFIRM BA/DEV]
- ...
```

---

## Checklist tự kiểm tra trước khi giao

**Format & Structure:**
- [ ] Tên file đúng `AI_ClaudeCode_API_<TênEndpoint>.xlsx`
- [ ] TC ID đúng `TC_{API_CODE}.{số thứ tự}` (ví dụ: TC_API.1, TC_API.2)
- [ ] Tất cả title bắt đầu bằng "Check"
- [ ] Group theo thứ tự chuẩn, bắt đầu bằng Authentication

**Pre-condition / Test Data (cột E):**
- [ ] Liệt kê token, data object, trạng thái DB cần có trước khi test
- [ ] Không ghi chung chung như "dữ liệu hợp lệ"
- [ ] Token naming rõ ràng: TOKEN_{ROLE}_{STATUS}
- [ ] Data object naming đúng convention: {Obj}_VALID_{N}, {Obj}_STATE_{TRANG_THAI}...

**Các Bước Thực Hiện (cột F):**
- [ ] Các bước đánh số thứ tự rõ ràng
- [ ] Ghi rõ Method + URL + Headers + Body/Params với giá trị data object cụ thể
- [ ] Mỗi TC write dùng data object RIÊNG (không share)

**Expected Result:**
- [ ] Dòng đầu luôn assert HTTP Status code
- [ ] Assert từng field trong response body với giá trị cụ thể
- [ ] Happy path: có DB side effect assertion
- [ ] Error case: assert đúng error code + message text

**Coverage:**
- [ ] Auth: cover đủ 5 case (A3)
- [ ] Validate: mỗi required field có TC riêng lẻ (A4)
- [ ] Idempotency: ghi rõ interval + DB assertion (A5)
- [ ] Network: chỉ rõ tool simulate (A6)
- [ ] Performance: ghi rõ concurrency + threshold (A7)
- [ ] BLOCKED tách riêng dòng, không lẫn với assertion đã biết

---

## Tham chiếu
- `references/api-auth-patterns.md` — Pattern TC cho các loại auth phổ biến
- `references/api-error-patterns.md` — Pattern TC cho error handling

---

## Automation Pipeline (Playwright Python)

Sau khi sinh TC xong bằng skill này, nếu user muốn **chạy automation**:

```
testcase-api-writer (sinh .xlsx TC)
        │
        ▼ (user muốn auto)
parse-tc-excel      ← đọc file .xlsx TC + API spec → MEMORY.md
        │
        ▼
implement-auto-api  ← đọc MEMORY.md → sinh Playwright Python
        │
        ▼
tests/*.py + conftest.py (chạy được ngay sau khi điền token + bundleId)
```

### Cột "Khả Năng Auto" — bắt buộc có trong file TC

Khi sinh TC bằng skill này, **bắt buộc thêm cột "Khả Năng Auto"** (cột cuối)
với 1 trong 3 giá trị:

| Giá trị | Ý nghĩa | Khi nào dùng |
|---------|---------|--------------|
| `✅ Auto được` | parse-tc-excel sinh đủ assertion, chạy thẳng | TC có expected rõ ràng, không phụ thuộc tool ngoài |
| `⚠️ Auto được một phần` | gen code nhưng có BLOCKED assumption | Expected còn chờ confirm BA/DEV, hoặc assert một phần |
| `❌ Khó auto` | không gen code Playwright | Cần JMeter/k6 (perf), Charles Proxy (network) |

### Quy tắc điền cột "Khả Năng Auto":

- **Authentication, Validate, Error Handling, Idempotency**: hầu hết `✅`
- **Business Rule có logic giá/location phức tạp**: `✅` nếu expected rõ, `⚠️` nếu còn BLOCKED
- **State Transition** yêu cầu admin action: `⚠️`
- **Data Consistency** cần DB query: `⚠️` (assert API được, DB assertion cần manual)
- **Performance** (concurrent, JMeter): `❌`
- **Network/Timeout** (Charles Proxy, tc netem): `❌`

> Điền cột này ngay khi viết TC — đừng để trống. Skill parse-tc-excel đọc cột
> này để quyết định FULL / PARTIAL / SKIP khi gen code.

# CLAUDE.md — ECOM API Auto Test

## Skills
Đọc SKILL.md tương ứng trước khi thực thi bất kỳ task nào.

| Skill | Path |
|-------|------|
| api-to-auto | ./skills/api-to-auto/SKILL.md |
| parse-tc-excel | ./skills/parse-tc-excel/SKILL.md |
| implement-auto-api | ./skills/implement-auto-api/SKILL.md |
| auto-bug-capture | ./skills/auto-bug-capture/SKILL.md |
| auto-bug-report | ./skills/auto-bug-report/SKILL.md |
| testcase-api-writer | ./skills/testcase-api-writer/SKILL.md |

## Project Info
- **Dự án:** ECOM Platform — API Auto Test
- **Base URL:** https://staging.tongdaiwifi.vn
- **Language:** Python + Playwright
- **Output dir:** ./outputs/

## Folder Convention
| Thư mục | Mục đích |
|---------|---------|
| `./00_input/` | Để file spec API vào đây (xlsx, pdf, link) |
| `./skills/` | Chứa toàn bộ skill pack — không sửa |
| `./playwright-api-tests/` | Code Playwright Python (sinh tự động) |
| `./bug-artifacts/` | Video + screenshot + error.json khi test fail |
| `./outputs/` | File Excel TC + bug report xuất ra đây |

## Ngôn ngữ
Trả lời bằng Tiếng Việt. Giữ tiếng Anh cho thuật ngữ kỹ thuật.

## Workflow
```
"Link spec → gen playwright đi"  →  api-to-auto  (4 phases tự động)
"gen bug report"                  →  auto-bug-report
```

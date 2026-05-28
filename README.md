# VibeTest_Tongdaiwifi

Hướng dẫn Push & Pull Git

  ---
  PUSH — Đưa code từ máy lên GitHub

  # Bước 1: Kiểm tra file nào đã thay đổi
  git status

  # Bước 2: Thêm file vào staging (chuẩn bị commit)
  git add .             # thêm tất cả file
  git add tên-file      # hoặc thêm từng file cụ thể

  # Bước 3: Commit (lưu thay đổi kèm mô tả)
  git commit -m "mô tả thay đổi của bạn"

  # Bước 4: Push lên GitHub
  git push

  ---
  PULL — Lấy code từ GitHub về máy

  # Lấy code mới nhất từ GitHub về
  git pull

  ---
  Quy trình thông thường hàng ngày

  Sáng đến làm → git pull          (lấy code mới nhất về)
  Làm việc...
  Xong việc    → git add .
                 git commit -m "..."
                 git push           (đẩy lên GitHub)

  ---
  Một số lệnh hữu ích khác

  ┌───────────────────┬────────────────────────────┐
  │       Lệnh        │          Tác dụng          │
  ├───────────────────┼────────────────────────────┤
  │ git status        │ Xem file nào đang thay đổi │
  ├───────────────────┼────────────────────────────┤
  │ git log --oneline │ Xem lịch sử commit         │
  ├───────────────────┼────────────────────────────┤
  │ git diff          │ Xem chi tiết thay đổi      │
  └───────────────────┴────────────────────────────┘

  ---
  Lưu ý: Luôn git pull trước khi bắt đầu làm việc để tránh xung đột code khi làm việc nhóm.

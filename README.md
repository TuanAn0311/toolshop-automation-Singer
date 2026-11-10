# toolshop-automation-Singer

Khung kiểm thử tự động Toolshop của nhóm Singer — Sprint 1.

## Cài đặt trên Windows PowerShell

Yêu cầu Python 3.12 và Git. Chạy trong thư mục repo:

```powershell
Copy-Item .env.example .env
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

`.env` chứa URL môi trường và được `.gitignore` loại trừ. Thiếu `BASE_URL`,
pytest báo `BASE_URL is not set. Copy .env.example to .env`.

## Chạy 4 smoke test

```powershell
.\.venv\Scripts\Activate.ps1
pytest -m smoke
pytest -m smoke --headed --slowmo 300
```

Nếu PowerShell chặn kích hoạt môi trường, dùng trực tiếp Python trong `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest -m smoke
.\.venv\Scripts\python.exe -m pytest -m smoke --headed --slowmo 300
```

| Test | Kết quả mong đợi |
| --- | --- |
| Tìm `pliers` | Có kết quả; mọi tên sản phẩm đều chứa `pliers` |
| Thêm `Claw Hammer`, số lượng 3 | Badge giỏ hàng hiển thị `3` |
| Đăng nhập bằng email không tồn tại | `Invalid email or password`, URL kết thúc `/auth/login` |
| Gửi form Contact trống | `Subject is required` và `Message is required` |

Mỗi test có một browser context mới. Test đăng nhập dùng email ngẫu nhiên
thuộc `example.com` để tránh khóa tài khoản dùng chung.

## Cấu trúc và quy tắc

- `conftest.py`, `pytest.ini`, `requirements.txt`, `.gitignore`, `.env.example`:
  chép từ repo thực hành, giữ nguyên phiên bản thư viện.
- `pages/`: đủ 7 page object từ nhánh `bai-giai` của
  [repo lớp](https://github.com/jameboykks/toolshop-practice/tree/bai-giai/pages).
- `tests/ui/test_smoke.py`: 4 test, mỗi test có marker `smoke`, `ui` và docstring
  3 dòng: mục tiêu, điều kiện, kết quả mong đợi.
- Locator và thao tác nằm trong `pages/`; assertion nằm trong test.

Ba lệnh sau phải không in ra kết quả:

```powershell
Select-String -Path tests\ui\*.py -Pattern "get_by_|locator\("
Select-String -Path pages\*.py -Pattern "expect\(|assert "
Select-String -Path tests\ui\*.py,pages\*.py -Pattern "sleep|wait_for_timeout"
```

## Pull Request và nghiệm thu

Mọi thay đổi đi qua nhánh `feature/ManhCuong-sprint1` và Pull Request vào `main`.
Tiêu đề PR: `Sprint 1: framework and smoke tests`. Mô tả ghi kết quả chạy thật
của `pytest -m smoke`.

Một thành viên khác kiểm tra locator, assertion, chờ cố định và docstring;
chọn **Approve** trước khi người mở PR merge. Chủ repo kiểm tra bảo vệ `main`
đã bật **Require a pull request before merging** và tối thiểu **1 approval**.

Khi nghiệm thu ngày 11/11: trình chiếu luật bảo vệ `main`, PR #1 đã merge
có approval của thành viên khác, rồi chạy `pytest -m smoke` để thấy `4 passed`.

# Triển khai trên Vercel

Dự án sau khi khởi tạo có sẵn một tệp `api/index.py` được runtime `@vercel/python` của Vercel nạp dưới dạng ứng dụng WSGI.

## 1. Khởi tạo và nhập dữ liệu cục bộ

```bash
lvt-honor init my-awards --non-interactive
cd my-awards
lvt-honor import results.csv --competition demo-a --year 2025 --replace
```

Tệp `data/<slug>.db` được commit kèm theo cấu hình để Vercel phục vụ. Với các đợt triển khai quy mô lớn, hãy thay SQLite bằng một cơ sở dữ liệu được host riêng; công cụ truy vấn nhận tham số `db_path`, nên việc viết một bộ chuyển đổi dùng connection pool chỉ là một thay đổi nhỏ.

## 2. Triển khai

```bash
npm i -g vercel
vercel deploy
```

Vercel tự động phát hiện điểm nhập `api/index.py`. Đặt các biến môi trường trong bảng điều khiển Vercel:

| Biến | Mục đích |
|------|---------|
| `PUBLIC_BASE_URL` | Origin của bạn, dạng `https://<project>.vercel.app` |
| `FORCE_HSTS` | `1` (Vercel đảm nhận đầu cuối TLS) |

## 3. Xác minh

```bash
curl https://<project>.vercel.app/health
# → {"ok":true}
```

## Ghi chú

- **Bề mặt quản trị**: theo mặc định, các bản triển khai trên Vercel đều công khai. Hãy bảo vệ `/admin` bằng tính năng chặn mật khẩu của Vercel (gói Pro), hoặc đặt `admin.enabled: false` trong cấu hình.
- **Cold start**: yêu cầu đầu tiên sau một khoảng nhàn rỗi sẽ kích hoạt hàm serverless khởi động lại (~200ms). Endpoint `/health` không phụ thuộc thành phần nào nên phù hợp cho các lượt thăm dò nhanh.

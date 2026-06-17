# Triển khai trên Vercel

Dự án được xây dựng bao gồm một `api/index.py` mà `@vercel/python` runtime của Vercel gắn kết như một ứng dụng WSGI.

## 1. Xây dựng + nhập cục bộ

```bash
lvt-honor init my-awards --non-interactive
cd my-awards
lvt-honor import results.csv --competition demo-a --year 2025 --replace
```

`data/<slug>.db` được cam kết cùng với cấu hình vì vậy Vercel phục vụ nó. (Đối với các triển khai quy mô lớn, hãy hoán đổi SQLite cho cơ sở dữ liệu được lưu trữ — công cụ truy vấn lấy `db_path`, vì vậy một bộ điều hợp nhóm kết nối là một thay đổi nhỏ.)

## 2. Triển khai

```bash
npm i -g vercel
vercel deploy
```

Vercel tự động phát hiện điểm nhập `api/index.py`. Đặt các biến môi trường trong bảng điều khiển Vercel:

| Biến | Mục đích |
|------|---------|
| `PUBLIC_BASE_URL` | `https://<project>.vercel.app` xuất xứ của bạn |
| `FORCE_HSTS` | `1` (Vercel chấm dứt TLS) |

## 3. Xác minh

```bash
curl https://<project>.vercel.app/health
# → {"ok":true}
```

## Ghi chú

- **Bề mặt quản trị viên**: Triển khai Vercel công khai theo mặc định. Gating `/admin` đằng sau bảo vệ mật khẩu của Vercel (gói Pro) hoặc đặt `admin.enabled: false` trong cấu hình.
- **Cold starts**: yêu cầu đầu tiên sau khi không hoạt động xoay chuyển chức năng serverless (~200ms). Điểm cuối `/health` không có phụ thuộc cho các bộ tiếp xúc nhanh.

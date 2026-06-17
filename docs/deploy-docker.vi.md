# Triển khai trên Docker

`Dockerfile` của gốc kho lưu trữ + `docker-compose.yml` xây dựng hình ảnh không phải root phục vụ cổng thông tin qua gunicorn trên cổng 8000.

## 1. Chuẩn bị thư mục dự án

Vùng chứa bind-mount `./project` để `/app/project`, vì vậy hãy đặt `honor.config.json` + `data/` của bạn ở đó:

```
project/
├── honor.config.json
└── data/
    └── <slug>.db      # tạo bởi lvt-honor import
```

Bạn có thể tạo những điều này trên máy chủ (không cần Python bên trong vùng chứa):

```bash
mkdir -p project/data
# ... sao chép honor.config.json + dữ liệu được gieo data/<slug>.db vào project/ ...
```

## 2. Xây dựng + chạy

```bash
cp .env.example .env      # đặt PUBLIC_BASE_URL
docker compose up -d --build
```

## 3. Xác minh

```bash
curl http://localhost:8000/health
# → {"ok":true}
```

Mở `http://localhost:8000` cho bảng vinh danh, `/search` và `/admin`.

## Ghi chú

- **Không phải root**: vùng chứa chạy như một người dùng hệ thống `app:app`.
- **Healthcheck**: kiểm tra `/health` (không có phụ thuộc) mỗi 30 giây.
- **Single worker**: `WEB_CONCURRENCY=1` vì kho SQLite mặc định không an toàn với nhiều quy trình. Để mở rộng theo chiều ngang, hãy chuyển kho đến máy chủ được chia sẻ và tăng `WEB_CONCURRENCY`.
- **Chỉnh sửa cấu hình**: thay đổi `project/honor.config.json` trên máy chủ, chạy `docker compose restart`. Không cần xây dựng lại.
- **Bề mặt quản trị viên**: đặt vùng chứa đằng sau proxy ngược (Nginx / Caddy / Traefik) với TLS + xác thực trước khi công khai `/admin`.

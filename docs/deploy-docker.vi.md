# Triển khai trên Docker

`Dockerfile` ở thư mục gốc của kho cùng với `docker-compose.yml` sẽ build một image chạy với quyền non-root, phục vụ cổng thông tin qua gunicorn trên cổng 8000.

## 1. Chuẩn bị thư mục dự án

Container sẽ bind-mount `./project` vào `/app/project`, vì vậy hãy đặt `honor.config.json` và thư mục `data/` của bạn vào đó:

```
project/
├── honor.config.json
└── data/
    └── <slug>.db      # tạo bởi lvt-honor import
```

Bạn có thể tạo các thư mục này ngay trên máy chủ (không cần Python bên trong container):

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

- **Non-root**: container chạy dưới người dùng hệ thống `app:app`.
- **Healthcheck**: kiểm tra `/health` (không phụ thuộc thành phần nào) sau mỗi 30 giây.
- **Một worker duy nhất**: đặt `WEB_CONCURRENCY=1` vì kho SQLite mặc định không an toàn khi chạy đa tiến trình. Để mở rộng theo chiều ngang, hãy chuyển kho dữ liệu sang một máy chủ dùng chung rồi tăng `WEB_CONCURRENCY`.
- **Chỉnh sửa cấu hình**: sửa `project/honor.config.json` trên máy chủ rồi chạy `docker compose restart`, không cần build lại.
- **Bề mặt quản trị**: đặt container sau một reverse proxy (Nginx / Caddy / Traefik) có TLS và xác thực trước khi công khai `/admin`.

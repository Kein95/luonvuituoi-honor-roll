# Bảo mật

Hướng dẫn bảo mật khi triển khai và vận hành LUONVUITUOI-HONOR ROLL.

## Tổng quan

Cổng thông tin được thiết kế theo mô hình **đọc công khai, ghi có kiểm soát** (read-public, write-gated):

- **Các trang công khai** (`/`, `/search`, `/hall-of-fame`, `/teams`) phục vụ lưu lượng từ khách truy cập chưa xác thực.
- **Khu vực quản trị** (`/admin`, `/api/admin/*`) yêu cầu xác thực bằng mật khẩu.
- Không công khai bất kỳ PII nào. Chỉ hiển thị tên, trường học, huy chương, môn học và thứ hạng.

## Xác thực quản trị

Xem [admin-auth.md](admin-auth.md) để biết mô hình xác thực đầy đủ.

Tóm tắt:

- Đăng nhập bằng một mật khẩu duy nhất, cấu hình qua biến môi trường `ADMIN_PASSWORD`.
- So sánh HMAC theo thời gian hằng định để ngăn tấn công phân tích thời gian.
- Cookie phiên Flask được ký, kèm cờ `HTTPOnly` và `SameSite=Lax`.
- Giới hạn tần suất chống tấn công vét cạn theo từng IP (có thể cấu hình, mặc định: 5 lần thử trong 60 giây).
- Token CSRF trên mọi biểu mẫu quản trị gửi bằng phương thức POST.
- Ghi nhật ký kiểm toán cho mọi lần đăng nhập thành công hoặc thất bại và mọi thao tác ghi của quản trị.

## Triển khai khu vực quản trị một cách an toàn

Theo mặc định, khu vực quản trị **chưa an toàn cho môi trường production**. Nếu công khai cổng thông tin, hãy đặt `/admin` sau một proxy ngược để kiểm soát truy cập:

### Tùy chọn 1: Proxy ngược với Basic Auth (Nginx)

```nginx
location /admin {
    auth_basic "Admin required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}

location /api/admin {
    auth_basic "Admin required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}
```

### Tùy chọn 2: Proxy ngược với OAuth (Caddy)

Sử dụng một plugin forward-auth, ví dụ `oauth2-proxy`:

```
https://example.com/admin {
    forward_auth localhost:4180 {
        uri /oauth2/auth
    }
    proxy / localhost:8000
}
```

### Tùy chọn 3: Tắt khu vực quản trị

Đặt `admin.enabled: false` trong cấu hình:

```json
"admin": { "enabled": false }
```

Khi đó, các yêu cầu đến `/login`, `/admin` và `/api/admin/*` đều trả về HTTP 404.

### Tùy chọn 4: Danh sách IP được phép

Sử dụng tường lửa hoặc proxy ngược để chỉ cho phép các IP quản trị nằm trong danh sách trắng:

```nginx
location /admin {
    allow 203.0.113.0/24;    # office network
    deny all;
    proxy_pass http://localhost:8000;
}
```

## Biến môi trường

Tuyệt đối không commit các biến này vào git; hãy dùng công cụ quản lý bí mật của nền tảng triển khai:

| Biến | Mục đích | Ví dụ |
|------|---------|-------|
| `ADMIN_PASSWORD` | Mật khẩu đăng nhập quản trị | `export ADMIN_PASSWORD="abc123xyz"` |
| `SECRET_KEY` | Ký cookie phiên | `export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"` |
| `PUBLIC_BASE_URL` | Origin công khai (dùng để kiểm tra origin của CSRF) | `https://example.com` |
| `FORCE_HSTS` | Bật header `Strict-Transport-Security` | `1` |
| `TRUST_PROXY_HEADERS` | Dùng `X-Forwarded-For` để xác định IP máy khách | `1` |
| `ADMIN_LOGIN_MAX_ATTEMPTS` | Số lần đăng nhập tối đa trước khi khóa (chống vét cạn) | `5` |
| `ADMIN_LOGIN_LOCKOUT_SECONDS` | Thời gian khóa khi vượt ngưỡng (chống vét cạn) | `60` |

## Bảo mật cơ sở dữ liệu

### Quyền tệp

Nếu chạy trên hệ thống dùng chung, hãy bảo vệ cơ sở dữ liệu SQLite:

```bash
chmod 600 data/honor.db
chmod 700 data/
```

### Sao lưu

- Mã hóa bản sao lưu cơ sở dữ liệu cả khi truyền đi lẫn khi lưu trữ.
- Cất giữ bản sao lưu ở nơi an toàn, có kiểm soát truy cập.
- Luân chuyển các bản sao lưu cũ (ví dụ: chỉ giữ lại 30 ngày gần nhất).

### Lưu giữ dữ liệu

Cổng thông tin không tự động xóa dữ liệu hết hạn. Nếu cần tuân thủ GDPR/CCPA, hãy xóa dữ liệu thủ công:

```bash
# Xóa tất cả các bản ghi cho một học sinh cụ thể (theo candidate_no)
sqlite3 data/honor.db "DELETE FROM achievements WHERE candidate_no = '12345';"

# Vacuum để thu hồi dung lượng
sqlite3 data/honor.db "VACUUM;"
```

## Bảo mật tầng truyền tải

### TLS

Luôn dùng HTTPS trong môi trường production. Hãy lấy chứng chỉ từ một tổ chức cấp chứng chỉ (CA) đáng tin cậy:

- **Vercel**: tự động cấp HTTPS qua Let's Encrypt.
- **Docker + Nginx**: dùng Certbot cho Let's Encrypt, hoặc chứng chỉ từ CA của bạn.
- **Docker + Traefik**: Traefik tự động gia hạn HTTPS.

### CSP (Content Security Policy)

Mỗi phản hồi HTML đều có một nonce riêng cho từng yêu cầu trong header `Content-Security-Policy`, qua đó chặn việc chèn mã kịch bản nội tuyến:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123...'; ...
```

Cơ chế này chặn các cuộc tấn công reflected XSS. Stored XSS không phải là rủi ro vì cổng thông tin chỉ lưu dữ liệu có cấu trúc (không lưu HTML do người dùng gửi lên).

### CORS

Cổng thông tin **không** trả về header CORS. Các trang công khai dành cho người dùng truy cập trực tiếp, không dành cho máy khách API. Nếu cần CORS, hãy bổ sung ở tầng proxy ngược.

## Xác thực đầu vào

### Bản ghi học sinh (khi nhập liệu)

- `candidate_no`, `name`, `school`, `subject_code`, `medal` được kiểm tra theo lược đồ cấu hình.
- Các mã cuộc thi hoặc huy chương bị thiếu hay không hợp lệ sẽ bị từ chối trong quá trình nhập.
- `data_mapping` giúp ngăn lỗi nhập sai cột: các cột được ánh xạ theo tên, không theo vị trí.

### Truy vấn tìm kiếm

- Tìm kiếm chấp nhận mọi chuỗi ký tự (UTF-8).
- Truy vấn dùng trong mệnh đề SQL `LIKE` đều được tham số hóa, qua đó ngăn tấn công SQL injection.
- Kết quả tìm kiếm được lọc theo lược đồ cấu hình (chỉ hiển thị các cuộc thi và năm hiện có).

### Dữ liệu nhập từ biểu mẫu (quản trị)

- Biểu mẫu mật khẩu quản trị chấp nhận mọi chuỗi ký tự.
- Mật khẩu được so sánh bằng `hmac.compare_digest()` (theo thời gian hằng định).
- Khi nhập CSV, hệ thống đối chiếu tên cột với `data_mapping` trước khi xử lý từng hàng.

## Ghi nhật ký và giám sát

### Dữ liệu nhạy cảm

- Mật khẩu **không bao giờ** bị ghi vào nhật ký.
- Nhật ký kiểm toán ghi lại hành động, IP và mốc thời gian, không ghi tên học sinh hay thông tin nhạy cảm.
- Stack trace của ngoại lệ chỉ được ghi ở mức DEBUG (không hiển thị trong môi trường production).

### Nhật ký hoạt động

Mọi thao tác quản trị đều được ghi lại trong bảng `admin_activity`:

- `admin.login.success` / `admin.login.failure`
- `achievement.add`
- `achievement.delete`

Truy vấn nhật ký:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC;"
```

## Những hạn chế đã biết

- **Không mã hóa dữ liệu khi lưu trữ**: cơ sở dữ liệu SQLite được lưu dưới dạng văn bản thuần trên ổ đĩa. Với dữ liệu rất nhạy cảm, hãy áp dụng mã hóa ở cấp hệ thống tệp (LUKS, FileVault, BitLocker).
- **Nhật ký kiểm toán không bất biến**: quản trị viên có quyền truy cập cơ sở dữ liệu có thể sửa hoặc xóa nhật ký kiểm toán. Để đáp ứng yêu cầu tuân thủ, hãy dùng một kho kiểm toán riêng chỉ cho phép ghi thêm (Cloudflare Logs, AWS CloudTrail, v.v.).
- **Thời lượng phiên**: phiên chỉ có hiệu lực trong vòng đời của tab trình duyệt. Nếu cần, hãy cân nhắc bổ sung thời gian chờ phiên rõ ràng (chẳng hạn 1 giờ không hoạt động).
- **Không giới hạn tần suất trên các endpoint công khai**: tìm kiếm, bộ lọc và chế độ xem thư viện không bị giới hạn. Với cổng thông tin công khai có lưu lượng cao, hãy bổ sung giới hạn tần suất ở proxy ngược.

## Báo cáo lỗ hổng bảo mật

Nếu phát hiện lỗ hổng bảo mật, vui lòng báo cáo một cách có trách nhiệm:

1. **Không** tạo issue công khai trên GitHub.
2. Gửi email riêng cho nhóm bảo trì theo chính sách bảo mật của kho mã (nếu đã được công bố).
3. Kèm theo mô tả chi tiết, bằng chứng khái niệm (proof of concept) và phương án khắc phục đề xuất.

Nhóm bảo trì sẽ phối hợp đưa ra bản vá và mốc thời gian công bố thông tin một cách có trách nhiệm.

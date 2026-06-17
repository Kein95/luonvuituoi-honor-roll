# Bảo mật

Hướng dẫn bảo mật để triển khai và vận hành LUONVUITUOI-HONOR ROLL.

## Tổng quát

Cổng thông tin được thiết kế như một hệ thống **read-public, write-gated**:

- **Các bề mặt công khai** (`/`, `/search`, `/hall-of-fame`, `/teams`) phục vụ lưu lượng khách truy cập chưa xác thực.
- **Bề mặt quản trị** (`/admin`, `/api/admin/*`) yêu cầu xác thực bằng mật khẩu.
- **Không PII** được công khai — chỉ tên, trường học, huy chương, môn học và xếp hạng.

## Xác thực quản trị

Xem [admin-auth.md](admin-auth.md) để biết mô hình xác thực đầy đủ.

Tóm tắt:

- Đăng nhập mật khẩu duy nhất qua biến môi trường `ADMIN_PASSWORD`.
- So sánh HMAC an toàn thời gian để ngăn chặn tấn công thời gian.
- Cookie phiên Flask được ký với cờ `HTTPOnly` và `SameSite=Lax`.
- Giới hạn tỷ lệ tấn công vũ phu trên mỗi IP (có thể cấu hình, mặc định: 5 lần cố gắng trong 60 giây).
- Mã thông báo CSRF trên tất cả các biểu mẫu quản trị POST.
- Ghi nhật ký kiểm toán về tất cả các thành công/thất bại đăng nhập và hành động ghi quản trị.

## Triển khai bề mặt quản trị một cách an toàn

Bề mặt quản trị **không an toàn sản xuất theo mặc định**. Nếu bạn công khai cổng thông tin, hãy gating `/admin` đằng sau proxy ngược:

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

Sử dụng một plugin forward-auth như `oauth2-proxy`:

```
https://example.com/admin {
    forward_auth localhost:4180 {
        uri /oauth2/auth
    }
    proxy / localhost:8000
}
```

### Tùy chọn 3: Vô hiệu hóa bề mặt quản trị

Đặt `admin.enabled: false` trong cấu hình của bạn:

```json
"admin": { "enabled": false }
```

Các yêu cầu đến `/login`, `/admin` và `/api/admin/*` trả về HTTP 404.

### Tùy chọn 4: Danh sách IP cho phép

Sử dụng tường lửa hoặc proxy ngược để tạo danh sách trắng các IP quản trị:

```nginx
location /admin {
    allow 203.0.113.0/24;    # office network
    deny all;
    proxy_pass http://localhost:8000;
}
```

## Biến môi trường

Không bao giờ cam kết chúng vào git; sử dụng quản lý bí mật của nền tảng triển khai của bạn:

| Biến | Mục đích | Ví dụ |
|------|---------|-------|
| `ADMIN_PASSWORD` | Mật khẩu đăng nhập quản trị | `export ADMIN_PASSWORD="abc123xyz"` |
| `SECRET_KEY` | Ký cookie phiên | `export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"` |
| `PUBLIC_BASE_URL` | Xuất xứ công khai (để kiểm tra nguồn gốc CSRF) | `https://example.com` |
| `FORCE_HSTS` | Bật tiêu đề `Strict-Transport-Security` | `1` |
| `TRUST_PROXY_HEADERS` | Sử dụng `X-Forwarded-For` cho IP máy khách | `1` |
| `ADMIN_LOGIN_MAX_ATTEMPTS` | Giới hạn tấn công vũ phu: max login attempts | `5` |
| `ADMIN_LOGIN_LOCKOUT_SECONDS` | Thời gian khóa tấn công vũ phu | `60` |

## Bảo mật cơ sở dữ liệu

### Quyền tệp

Nếu chạy trên hệ thống dùng chung, hãy bảo vệ cơ sở dữ liệu SQLite:

```bash
chmod 600 data/honor.db
chmod 700 data/
```

### Sao lưu

- Mã hóa sao lưu cơ sở dữ liệu trong quá trình chuyển và khi đang lưu trữ.
- Lưu trữ sao lưu ở một vị trí an toàn, được kiểm soát truy cập.
- Xoay vòng các bản sao lưu cũ (ví dụ: giữ 30 ngày cuối cùng).

### Giữ lại dữ liệu

Cổng thông tin không thực hiện hết hạn dữ liệu tự động. Nếu cần tuân thủ GDPR/CCPA, hãy thực hiện quá trình xóa thủ công:

```bash
# Xóa tất cả các bản ghi cho một học sinh cụ thể (theo candidate_no)
sqlite3 data/honor.db "DELETE FROM achievements WHERE candidate_no = '12345';"

# Vacuum để lấy lại không gian
sqlite3 data/honor.db "VACUUM;"
```

## Bảo mật vận chuyển

### TLS

Luôn sử dụng HTTPS trong sản xuất. Lấy chứng chỉ từ Cơ quan cấp chứng chỉ đáng tin cậy:

- **Vercel** — tự động cấp phát HTTPS qua Let's Encrypt.
- **Docker + Nginx** — sử dụng Certbot cho Let's Encrypt hoặc chứng chỉ CA của bạn.
- **Docker + Traefik** — Traefik tự động gia hạn HTTPS.

### CSP (Content Security Policy)

Mỗi phản hồi HTML đều bao gồm nonce trên mỗi yêu cầu trong tiêu đề `Content-Security-Policy`, ngăn chặn tiêm kịch bản nội tuyến:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123...'; ...
```

Điều này chặn các cuộc tấn công XSS được phản ánh. XSS được lưu trữ không phải là rủi ro vì cổng thông tin chỉ lưu trữ dữ liệu có cấu trúc (không HTML do người dùng gửi).

### CORS

Cổng thông tin **không** hiển thị tiêu đề CORS. Các bề mặt công khai là cho những khách truy cập con người, không phải cho các máy khách API. Nếu bạn cần CORS, hãy thêm nó ở mức proxy ngược.

## Xác thực đầu vào

### Bản ghi học sinh (nhập)

- `candidate_no`, `name`, `school`, `subject_code`, `medal` được xác thực bằng lược đồ cấu hình.
- Các mã cuộc thi/huy chương bị thiếu hoặc không được công nhận sẽ bị từ chối trong quá trình nhập.
- `data_mapping` ngăn chặn tiêm đầu tiên — các cột được ánh xạ theo tên, không phải theo vị trí.

### Truy vấn tìm kiếm

- Tìm kiếm chấp nhận bất kỳ chuỗi nào (UTF-8).
- Truy vấn được sử dụng trong mệnh đề SQL `LIKE` được tham số hóa, ngăn chặn tiêm SQL.
- Kết quả tìm kiếm được lọc bằng lược đồ cấu hình (chỉ các cuộc thi/năm hiện có được hiển thị).

### Đầu vào biểu mẫu (quản trị)

- Biểu mẫu mật khẩu quản trị chấp nhận bất kỳ chuỗi nào.
- Mật khẩu được so sánh với `hmac.compare_digest()` (thời gian không đổi).
- Nhập CSV xác thực tên cột so với `data_mapping` trước khi xử lý hàng.

## Ghi nhật ký và giám sát

### Dữ liệu nhạy cảm

- Mật khẩu **không bao giờ** được ghi nhật ký.
- Nhật ký kiểm toán ghi lại hành động, IP và dấu thời gian — không phải tên học sinh hoặc chi tiết.
- Stack trace ngoại lệ được ghi lại ở mức DEBUG (không hiển thị trong sản xuất).

### Nhật ký hoạt động

Tất cả các hành động quản trị được ghi lại trong bảng `admin_activity`:

- `admin.login.success` / `admin.login.failure`
- `achievement.add`
- `achievement.delete`

Truy vấn nhật ký:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC;"
```

## Những hạn chế đã biết

- **Không có mã hóa dữ liệu khi đang lưu trữ** — cơ sở dữ liệu SQLite được lưu trữ dưới dạng văn bản thuần túy trên đĩa. Đối với dữ liệu rất nhạy cảm, hãy áp dụng mã hóa cấp hệ thống tệp (LUKS, FileVault, BitLocker).
- **Không có tính bất biến của nhật ký kiểm toán** — quản trị viên có quyền truy cập cơ sở dữ liệu có thể chỉnh sửa hoặc xóa nhật ký kiểm toán. Để tuân thủ, hãy sử dụng kho kiểm toán chỉ nối thêm riêng (Cloudflare Logs, AWS CloudTrail, v.v.).
- **Thời lượng phiên** — các phiên có giá trị cho vòng đời của tab trình duyệt. Hãy xem xét thêm thời gian chờ phiên rõ ràng (ví dụ: 1 giờ không hoạt động) nếu cần.
- **Không giới hạn tỷ lệ trên các điểm cuối công khai** — tìm kiếm, bộ lọc và chế độ xem thư viện không được điều chỉnh. Đối với các cổng thông tin công khai có lưu lượng cao, hãy thêm giới hạn tỷ lệ ở proxy ngược.

## Báo cáo các vấn đề bảo mật

Nếu bạn phát hiện ra lỗ hổng bảo mật, vui lòng báo cáo một cách có trách nhiệm:

1. **Không** mở một vấn đề GitHub công khai.
2. Gửi email cho các nhà bảo trì riêng tư qua chính sách bảo mật của kho lưu trữ (nếu được xuất bản).
3. Bao gồm mô tả chi tiết, bằng chứng khái niệm và giảm nhẹ được đề xuất.

Những nhà bảo trì sẽ phối hợp một bản sửa chữa và dòng thời gian tiết lộ có trách nhiệm.

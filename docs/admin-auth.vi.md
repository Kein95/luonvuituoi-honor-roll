# Xác thực quản trị

Bảng vinh danh sử dụng cơ chế đăng nhập bằng một mật khẩu duy nhất, được kiểm tra qua so sánh HMAC theo thời gian hằng định để ngăn các cuộc tấn công phân tích thời gian.

## Luồng đăng nhập

1. Truy cập `https://<your-portal>/login`.
2. Nhập mật khẩu quản trị (cấu hình qua biến môi trường `ADMIN_PASSWORD`).
3. Nhấp **Đăng nhập**. Nếu thành công, hệ thống cấp một cookie phiên Flask đã được ký.
4. Phiên có hiệu lực trong tab trình duyệt. Đóng tab sẽ tự động đăng xuất.

## Cấu hình mật khẩu

**Bắt buộc.** Mật khẩu quản trị chỉ được đọc từ biến môi trường, không bao giờ đọc từ tệp cấu hình đã commit:

```bash
export ADMIN_PASSWORD="your-secure-password-here"
```

Để đổi mật khẩu, hãy khởi động lại ứng dụng với giá trị `ADMIN_PASSWORD` mới. Mọi phiên đang hoạt động vẫn có hiệu lực cho đến khi trình duyệt được đóng.

## Tính năng bảo mật

### So sánh theo thời gian hằng định

Mật khẩu được kiểm tra bằng `hmac.compare_digest()`, một phép so sánh có thời gian thực thi hằng định. Cơ chế này ngăn kẻ theo dõi suy ra độ dài hoặc nội dung mật khẩu thông qua phân tích thời gian phản hồi. Ngay cả với mật khẩu không hợp lệ, máy chủ vẫn thực hiện đúng khối lượng tính toán mật mã đó trước khi từ chối đăng nhập.

### Cookie phiên

Phiên được lưu trong cookie Flask đã ký, kèm các lớp bảo vệ sau:

- **`SESSION_COOKIE_HTTPONLY=True`**: token phiên không bao giờ truy cập được từ JavaScript, qua đó chặn đường rò rỉ token qua XSS.
- **`SESSION_COOKIE_SAMESITE="Lax"`**: cookie không được gửi kèm trong các yêu cầu liên trang (cross-site), giúp giảm thiểu nguy cơ CSRF.
- **`SECRET_KEY`**: dùng để ký cookie. Nếu không đặt, hệ thống tạo một khóa ngẫu nhiên tạm thời (phiên sẽ mất khi khởi động lại). Với môi trường production, hãy đặt một khóa cố định:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

### Chính sách bảo mật nội dung (CSP)

Mọi phản hồi HTML đều có header `Content-Security-Policy` kèm nonce riêng cho từng yêu cầu, qua đó chặn việc chèn mã kịch bản nội tuyến.

## Tắt khu vực quản trị

Đặt `admin.enabled: false` trong `honor.config.json` để tắt toàn bộ khu vực quản trị:

```json
"admin": { "enabled": false, "auth_mode": "password" }
```

Khi đó, các yêu cầu đến `/login`, `/admin` hoặc `/api/admin/*` đều trả về HTTP 404.

## Tính năng tăng cường (đang phát triển)

Các tính năng sau đang được bổ sung song song và đã có mặt trong các bản dựng hiện tại:

### Giới hạn tần suất chống đăng nhập vét cạn

Bộ giới hạn tần suất theo từng IP giúp ngăn các cuộc tấn công đoán mật khẩu:

- Sau `N` lần đăng nhập thất bại (mặc định: 5), IP bị khóa trong `M` giây (mặc định: 60).
- Số lần thất bại được đếm theo từng địa chỉ IP, không theo người dùng (vì biểu mẫu đăng nhập không yêu cầu tên đăng nhập).
- Bộ đếm thời gian khóa được đặt lại sau mỗi lần thử thất bại.

Cấu hình qua các biến môi trường:

```bash
export ADMIN_LOGIN_MAX_ATTEMPTS=5
export ADMIN_LOGIN_LOCKOUT_SECONDS=60
```

### Token CSRF trên các biểu mẫu quản trị POST

Mọi biểu mẫu quản trị (`<form method="POST">`) đều có một trường ẩn chứa token CSRF. Máy chủ xác minh token này trước khi xử lý bất kỳ thao tác ghi nào:

- Token gắn với phiên đăng nhập và được cấp mới mỗi khi đăng nhập hoặc đăng xuất.
- API ghi của quản trị (`/api/admin/*`) yêu cầu đúng token đó trong header `X-CSRF-Token`; nếu thiếu hoặc sai sẽ trả về HTTP 403 (Forbidden). Riêng biểu mẫu đăng nhập, nếu thiếu token sẽ trả về HTTP 400.
- Cơ chế này ngăn các yêu cầu giả mạo liên trang (cross-site) xuất phát từ trang của kẻ tấn công.

### Ghi nhật ký kiểm toán cho việc đăng nhập và thao tác quản trị

Mọi thao tác quản trị đều được ghi lại:

- **Đăng nhập thành công**: mốc thời gian, địa chỉ IP, thời điểm bắt đầu phiên.
- **Đăng nhập thất bại**: mốc thời gian, địa chỉ IP, lý do (sai mật khẩu, bị khóa, v.v.).
- **Thao tác ghi của quản trị**: mốc thời gian, IP, hành động (thêm thành tích, xóa thành tích), ID học sinh liên quan.

Nhật ký được lưu trong cơ sở dữ liệu SQLite (bảng `admin_activity`) và có thể đọc bằng SQL:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity ORDER BY timestamp DESC LIMIT 20;"
```

## Giao ước của tầng truyền tải

Bất kỳ trình xử lý nào gọi đến endpoint đăng nhập đều **phải**:

1. Kiểm tra kích thước yêu cầu trước khi phân tích (ứng dụng Flask giới hạn ở mức tối đa 32 KB).
2. Bắt lỗi xác thực và chuyển thành HTTP 401.
3. Phát header CSP kèm nonce trên các phản hồi HTML.

Máy chủ phát triển (`lvt-honor dev`) và trình xử lý trên Vercel (`api/index.py`) đều tuân thủ các giao ước này. Các tầng truyền tải tùy chỉnh cũng nên áp dụng cùng một khuôn mẫu.

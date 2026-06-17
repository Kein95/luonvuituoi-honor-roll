# Xác thực quản trị

Bảng vinh danh sử dụng một sơ đồ đăng nhập dựa trên mật khẩu duy nhất, được kiểm tra bằng so sánh HMAC an toàn thời gian để ngăn chặn các cuộc tấn công thời gian.

## Luồng đăng nhập

1. Điều hướng đến `https://<your-portal>/login`.
2. Nhập mật khẩu quản trị (đặt thông qua biến môi trường `ADMIN_PASSWORD`).
3. Nhấp **Đăng nhập**. Nếu thành công, một cookie phiên làm việc Flask được ký sẽ được cấp.
4. Phiên có giá trị cho tab trình duyệt. Đóng tab sẽ đăng xuất bạn.

## Cấu hình mật khẩu

**Bắt buộc.** Mật khẩu quản trị được đọc từ môi trường chỉ. Không bao giờ được đọc từ cấu hình được cam kết:

```bash
export ADMIN_PASSWORD="your-secure-password-here"
```

Thay đổi mật khẩu bằng cách khởi động lại ứng dụng bằng giá trị `ADMIN_PASSWORD` mới. Tất cả các phiên hoạt động vẫn có giá trị cho đến khi trình duyệt bị đóng.

## Tính năng bảo mật

### So sánh an toàn thời gian

Mật khẩu được kiểm tra bằng `hmac.compare_digest()`, một so sánh thời gian không đổi. Điều này ngăn chặn người quan sát suy ra độ dài hoặc nội dung mật khẩu thông qua phân tích thời gian phản ứng. Ngay cả đối với mật khẩu không hợp lệ, máy chủ cũng thực hiện công việc mật mã giống nhau trước khi từ chối đăng nhập.

### Cookie phiên làm việc

Các phiên được lưu trữ trong các cookie Flask được ký với các bảo vệ sau:

- **`SESSION_COOKIE_HTTPONLY=True`**: mã thông báo phiên không bao giờ có thể truy cập được từ JavaScript, đóng cửa đường dẫn dẫn xuất XSS.
- **`SESSION_COOKIE_SAMESITE="Lax"`**: các cookie không được gửi trên các yêu cầu giữa các trang web, giảm nhẹ CSRF.
- **`SECRET_KEY`**: ký cookie. Nếu không được đặt, một khóa tạm thời ngẫu nhiên sẽ được tạo (phiên sẽ bị mất khi khởi động lại). Đối với sản xuất, hãy đặt khóa ổn định:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

### Chính sách bảo mật nội dung

Mọi phản hồi HTML đều bao gồm tiêu đề `Content-Security-Policy` có nonce cho mỗi yêu cầu, ngăn chặn tiêm kịch bản nội tuyến.

## Vô hiệu hóa quản trị

Đặt `admin.enabled: false` trong `honor.config.json` của bạn để tắt toàn bộ bề mặt quản trị:

```json
"admin": { "enabled": false, "auth_mode": "password" }
```

Các yêu cầu đến `/login`, `/admin` hoặc `/api/admin/*` trả về HTTP 404.

## Tính năng tăng cường (đang phát triển)

Các tính năng sau đây đang được thêm vào đồng thời và có trong các bản dựng hiện tại:

### Giới hạn tỷ lệ tấn công vũ phu đăng nhập

Bộ giới hạn tỷ lệ trên mỗi IP ngăn chặn các cuộc tấn công đoán mật khẩu:

- Sau `N` lần đăng nhập không thành công (mặc định: 5), IP bị khóa trong `M` giây (mặc định: 60).
- Các lần cố gắng không thành công được theo dõi trên mỗi địa chỉ IP, không phải theo người dùng (vì biểu mẫu đăng nhập không yêu cầu tên người dùng).
- Bộ đếm thời gian hết hạn được đặt lại sau mỗi lần cố gắng không thành công.

Cấu hình thông qua các biến môi trường:

```bash
export ADMIN_LOGIN_MAX_ATTEMPTS=5
export ADMIN_LOGIN_LOCKOUT_SECONDS=60
```

### Mã thông báo CSRF trên các biểu mẫu quản trị POST

Tất cả các biểu mẫu quản trị (`<form method="POST">`) đều bao gồm một trường mã thông báo CSRF ẩn. Máy chủ xác minh mã thông báo trước khi xử lý bất kỳ hoạt động ghi nào:

- Mã thông báo gắn với phiên đăng nhập và được xoay mới mỗi khi bạn đăng nhập hoặc đăng xuất.
- API ghi quản trị (`/api/admin/*`) yêu cầu cùng mã thông báo trong header `X-CSRF-Token`; thiếu hoặc sai sẽ trả về HTTP 403 (Forbidden). Biểu mẫu đăng nhập từ chối khi thiếu mã với HTTP 400.
- Điều này ngăn chặn yêu cầu giả mạo giữa các trang web từ trang của kẻ tấn công.

### Ghi nhật ký kiểm toán về thành công/thất bại đăng nhập và hoạt động quản trị

Mọi hoạt động quản trị được ghi lại:

- **Đăng nhập thành công**: dấu thời gian, địa chỉ IP, bắt đầu phiên.
- **Đăng nhập không thành công**: dấu thời gian, địa chỉ IP, lý do (mật khẩu không chính xác, khóa, v.v.).
- **Ghi quản trị**: dấu thời gian, IP, hành động (thêm thành tích, xóa thành tích), ID học sinh mục tiêu.

Nhật ký được duy trì trong cơ sở dữ liệu SQLite (bảng `admin_activity`) và có thể đọc bằng SQL:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity ORDER BY timestamp DESC LIMIT 20;"
```

## Hợp đồng lớp vận chuyển

Bất kỳ trình xử lý nào gọi điểm cuối đăng nhập **phải**:

1. Xác thực kích thước yêu cầu trước khi phân tích (ứng dụng Flask làm điều này tối đa 32 KB).
2. Bắt lỗi xác thực và dịch sang HTTP 401.
3. Phát hành tiêu đề CSP với nonce trên các phản hồi HTML.

Máy chủ phát triển (`lvt-honor dev`) và trình xử lý Vercel (`api/index.py`) đều thực hiện các hợp đồng này. Các vận chuyển tùy chỉnh nên tuân theo cùng một mẫu.

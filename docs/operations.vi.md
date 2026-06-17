# Vận hành

Cách chạy triển khai LUONVUITUOI-HONOR ROLL từng ngày: kiểm tra sức khỏe, bề mặt nhật ký, lựa chọn cơ sở dữ liệu và danh sách kiểm tra sự cố.

## Kiểm tra sức khỏe

```http
GET /health
```

Trả về `{"ok": true}` với HTTP 200. Điểm cuối:

- **Không** đọc cơ sở dữ liệu.
- **Không** ghi bất kỳ trạng thái nào.
- Không có yêu cầu xác thực.

Docker `HEALTHCHECK`, Kubernetes liveness và các bộ tiếp xúc cân bằng tải nên nhắm mục tiêu đến đường dẫn này.

## Nhật ký

Mọi thứ chảy qua mô-đun `logging` stdlib ở mức `WARNING` trở lên. Trong Docker, những điều đó được chuyển đến stdout và được `docker logs` ghi lại. Trên Vercel, hãy sử dụng `vercel logs --follow` để truyền phát chúng.

Những thông báo to lớn đáng để cảnh báo:

| Logger | Thông báo | Ý nghĩa |
|--------|-----------|--------|
| `luonvuitoi_honor_cli.server.app` | `ADMIN_PASSWORD not set` | Đăng nhập quản trị bị tắt. Đặt biến env để bật nó. |
| `luonvuitoi_honor.config` | `Cross-field validation failed` | `honor.config.json` có lỗi cấu trúc (ví dụ: một huy chương được tham chiếu không tồn tại). Cổng thông tin sẽ không khởi động. |

Các lỗi được xử lý (tìm kiếm 404, bộ lọc không hợp lệ) không được ghi lại. Chúng là lưu lượng bình thường.

## Cơ sở dữ liệu

Cổng thông tin lưu trữ các thành tích trong cơ sở dữ liệu SQLite tại `data/<slug>.db` (đường dẫn được xác định bởi `honor.config.json#project.slug` của bạn).

### Vòng đời dữ liệu

- **Gieo hạt**: sử dụng `lvt-honor seed` để tạo dữ liệu giả để kiểm tra cục bộ.
- **Nhập**: sử dụng `lvt-honor import <file>` để tải các thành tích từ CSV/Excel/JSON.
- **Xóa**: sử dụng bảng điều khiển quản trị (`/admin`) hoặc các lệnh SQLite trực tiếp.
- **Sao lưu**: sao chép `data/<slug>.db` sang một vị trí an toàn.

### Truy vấn cơ sở dữ liệu

```bash
# Liệt kê tất cả các thành tích cho một cuộc thi và năm cụ thể
sqlite3 data/honor.db "SELECT name, school, medal, subject_code FROM achievements WHERE competition_id = 'demo-a' AND year = 2025 ORDER BY name;"

# Đếm huy chương theo cấp
sqlite3 data/honor.db "SELECT medal, COUNT(*) FROM achievements WHERE year = 2025 GROUP BY medal;"

# Tìm học sinh trùng lặp (cùng candidate_no, tên khác nhau). Kiểm tra chất lượng dữ liệu
sqlite3 data/honor.db "SELECT candidate_no, COUNT(DISTINCT name) FROM achievements GROUP BY candidate_no HAVING COUNT(DISTINCT name) > 1;"

# Xem hoạt động quản trị (thành công/thất bại đăng nhập, hành động ghi)
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity ORDER BY timestamp DESC LIMIT 20;"
```

### An toàn đa quy trình

Theo mặc định, cổng thông tin sử dụng khóa tích hợp của SQLite. **Nếu chạy nhiều worker** (`WEB_CONCURRENCY > 1`), hãy đảm bảo:

- SQLite tệp duy nhất trên hệ thống tệp cục bộ (không phải NFS hoặc mount mạng), HOẶC
- Di chuyển sang cơ sở dữ liệu PostgreSQL (yêu cầu bộ điều hợp lược đồ, chưa được vận chuyển).

Nhật ký khởi động cảnh báo nếu bạn định cấu hình sai:

```
SQLite is not safe with 4 workers. Either drop to WEB_CONCURRENCY=1 or migrate to PostgreSQL.
```

## Thông tin đăng nhập quản trị

### Đặt mật khẩu

```bash
export ADMIN_PASSWORD="your-secure-password"
```

Mật khẩu không được lưu trữ trong cấu hình được cam kết. Nó được đọc từ môi trường chỉ. Điều này đảm bảo mật khẩu không bao giờ được cam kết vô tình vào git.

### Thay đổi mật khẩu

Khởi động lại ứng dụng bằng `ADMIN_PASSWORD` mới. Các phiên hoạt động vẫn hợp lệ cho đến khi người dùng đóng tab trình duyệt của họ.

### Vô hiệu hóa bề mặt quản trị

Đặt `admin.enabled: false` trong `honor.config.json`:

```json
"admin": { "enabled": false }
```

Các yêu cầu đến `/login`, `/admin` và `/api/admin/*` trả về HTTP 404.

## Tải lại cấu hình nóng

Chỉnh sửa `honor.config.json` trong khi cổng thông tin đang chạy:

- **Docker:** cập nhật `project/honor.config.json` trên máy chủ, sau đó `docker compose restart`.
- **Vercel:** cập nhật cấu hình trong mã nguồn của bạn, triển khai lại hoặc sử dụng ghi đè biến môi trường của Vercel (nếu cấu hình được tham số hóa).
- **Dev cục bộ**: cổng thông tin tải lại trên mỗi yêu cầu, chỉ cần lưu tệp.

Nếu cấu hình mới không hợp lệ, cổng thông tin trả về HTTP 500 với thông báo lỗi xác thực.

## Danh sách kiểm tra giám sát

- [ ] **Kiểm tra sức khỏe thành công**: `curl https://<portal>/health` trả về 200.
- [ ] **Tìm kiếm hoạt động**: `/search?q=<name>` trả về kết quả hoặc "not found", không phải lỗi.
- [ ] **Đăng nhập quản trị hoạt động**: `/login` chấp nhận mật khẩu và cấp quyền truy cập vào `/admin`.
- [ ] **Bộ lọc hoạt động**: menu thả xuống cuộc thi, năm, huy chương, môn học thu hẹp kết quả.
- [ ] **Nhập thành công**: `lvt-honor import <file>` báo cáo số hàng.
- [ ] **Nhật ký sạch**: `docker logs <container>` không hiển thị dòng `ERROR` hoặc `CRITICAL`.
- [ ] **Cơ sở dữ liệu có thể truy cập được**: `sqlite3 data/honor.db ".tables"` liệt kê lược đồ.

## Phản ứng sự cố

| Triệu chứng | Chẩn đoán | Sửa chữa |
|------------|----------|---------|
| `/health` trả về 500 | Cấu hình không hợp lệ hoặc cơ sở dữ liệu bị hỏng. | Kiểm tra nhật ký; xác thực `honor.config.json` bằng lược đồ. Khôi phục cơ sở dữ liệu từ sao lưu nếu cần. |
| Vòng lặp đăng nhập quản trị (mật khẩu luôn sai) | `ADMIN_PASSWORD` không được đặt hoặc đánh máy sai trong env. | Xác minh biến env khớp với mật khẩu của bạn chính xác. |
| Nhập báo cáo "cột không tìm thấy" | Tiêu đề CSV không khớp với `data_mapping` trong cấu hình. | Kiểm tra tên cột trong CSV và cập nhật `data_mapping` trong cấu hình. |
| Tìm kiếm không trả về kết quả, nhưng học sinh tồn tại | Bộ lọc quá hẹp; hãy thử đặt lại chúng bằng nút **Đặt lại**. | Hoặc tên học sinh được nhập với lỗi đánh máy; sử dụng bảng điều khiển quản trị để xác minh dữ liệu. |
| Hết không gian đĩa | Cơ sở dữ liệu SQLite đã phát triển quá lớn hoặc các tệp tạm thời đang tích tụ. | Lưu trữ dữ liệu cũ, xóa các tệp tạm thời hoặc nâng cấp lưu trữ. |

## Mở rộng

- **Triển khai một hộp**: `WEB_CONCURRENCY=1`, tệp SQLite trên đĩa cục bộ. Phù hợp với tối đa khoảng 50k học sinh.
- **Nhiều worker**: di chuyển sang PostgreSQL, đặt `WEB_CONCURRENCY=4` hoặc cao hơn. Phù hợp với bất kỳ quy mô nào.

Công cụ truy vấn bị ràng buộc I/O, không bị ràng buộc CPU. Thêm lõi chỉ giúp nếu cơ sở dữ liệu ở xa và bị ràng buộc độ trễ. Đối với hầu hết các triển khai, một worker duy nhất với lưu trữ cục bộ nhanh là đủ.

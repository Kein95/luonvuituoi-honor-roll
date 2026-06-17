# Vận hành

Hướng dẫn vận hành một bản triển khai LUONVUITUOI-HONOR ROLL hằng ngày: kiểm tra tình trạng hoạt động, nơi xem nhật ký, lựa chọn cơ sở dữ liệu và danh sách kiểm tra khi có sự cố.

## Kiểm tra sức khỏe

```http
GET /health
```

Trả về `{"ok": true}` với HTTP 200. Điểm cuối:

- **Không** đọc cơ sở dữ liệu.
- **Không** ghi bất kỳ trạng thái nào.
- Không có yêu cầu xác thực.

Docker `HEALTHCHECK`, liveness probe của Kubernetes và các lượt thăm dò từ bộ cân bằng tải đều nên trỏ tới đường dẫn này.

## Nhật ký

Mọi thứ đều được ghi qua mô-đun `logging` của thư viện chuẩn ở mức `WARNING` trở lên. Trong Docker, các log này được đưa ra stdout và `docker logs` thu lại. Trên Vercel, hãy dùng `vercel logs --follow` để xem trực tiếp.

Những thông báo nổi bật đáng để thiết lập cảnh báo:

| Logger | Thông báo | Ý nghĩa |
|--------|-----------|--------|
| `luonvuitoi_honor_cli.server.app` | `ADMIN_PASSWORD not set` | Đăng nhập quản trị đang bị tắt. Đặt biến môi trường để bật lên. |
| `luonvuitoi_honor.config` | `Cross-field validation failed` | `honor.config.json` có lỗi cấu trúc (ví dụ: tham chiếu tới một huy chương không tồn tại). Cổng thông tin sẽ không khởi động. |

Các lỗi đã được xử lý (tìm kiếm trả về 404, bộ lọc không hợp lệ) thì không ghi lại, vì đó là truy cập bình thường.

## Cơ sở dữ liệu

Cổng thông tin lưu trữ các thành tích trong cơ sở dữ liệu SQLite tại `data/<slug>.db` (đường dẫn được xác định bởi `honor.config.json#project.slug` của bạn).

### Vòng đời dữ liệu

- **Tạo dữ liệu mẫu**: dùng `lvt-honor seed` để sinh dữ liệu giả phục vụ kiểm thử cục bộ.
- **Nhập dữ liệu**: dùng `lvt-honor import <file>` để nạp thành tích từ CSV/Excel/JSON.
- **Xóa**: dùng bảng điều khiển quản trị (`/admin`) hoặc các lệnh SQLite trực tiếp.
- **Sao lưu**: sao chép `data/<slug>.db` sang một nơi an toàn.

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

Theo mặc định, cổng thông tin dùng cơ chế khóa tích hợp sẵn của SQLite. **Nếu chạy nhiều worker** (`WEB_CONCURRENCY > 1`), hãy đảm bảo một trong hai điều sau:

- Dùng SQLite một tệp duy nhất trên hệ thống tệp cục bộ (không phải NFS hay ổ mạng), HOẶC
- Chuyển sang cơ sở dữ liệu PostgreSQL (cần một bộ chuyển đổi schema, hiện chưa được cung cấp).

Nhật ký khởi động sẽ cảnh báo nếu bạn cấu hình sai:

```
SQLite is not safe with 4 workers. Either drop to WEB_CONCURRENCY=1 or migrate to PostgreSQL.
```

## Thông tin đăng nhập quản trị

### Đặt mật khẩu

```bash
export ADMIN_PASSWORD="your-secure-password"
```

Mật khẩu không được lưu trong tệp cấu hình được commit, mà chỉ được đọc từ biến môi trường. Nhờ vậy, mật khẩu không bao giờ vô tình bị commit vào git.

### Thay đổi mật khẩu

Khởi động lại ứng dụng với `ADMIN_PASSWORD` mới. Các phiên đang hoạt động vẫn còn hiệu lực cho đến khi người dùng đóng tab trình duyệt.

### Vô hiệu hóa bề mặt quản trị

Đặt `admin.enabled: false` trong `honor.config.json`:

```json
"admin": { "enabled": false }
```

Các yêu cầu đến `/login`, `/admin` và `/api/admin/*` trả về HTTP 404.

## Tải lại cấu hình nóng

Chỉnh sửa `honor.config.json` trong khi cổng thông tin đang chạy:

- **Docker:** cập nhật `project/honor.config.json` trên máy chủ, sau đó `docker compose restart`.
- **Vercel:** cập nhật cấu hình trong mã nguồn rồi triển khai lại, hoặc dùng cơ chế ghi đè biến môi trường của Vercel (nếu cấu hình đã được tham số hóa).
- **Dev cục bộ**: cổng thông tin tự nạp lại sau mỗi yêu cầu, bạn chỉ cần lưu tệp.

Nếu cấu hình mới không hợp lệ, cổng thông tin trả về HTTP 500 với thông báo lỗi xác thực.

## Danh sách kiểm tra giám sát

- [ ] **Kiểm tra sức khỏe đạt**: `curl https://<portal>/health` trả về 200.
- [ ] **Tìm kiếm hoạt động**: `/search?q=<name>` trả về kết quả hoặc "not found", chứ không phải lỗi.
- [ ] **Đăng nhập quản trị hoạt động**: `/login` chấp nhận mật khẩu và cấp quyền truy cập vào `/admin`.
- [ ] **Bộ lọc hoạt động**: menu thả xuống cuộc thi, năm, huy chương, môn học thu hẹp kết quả.
- [ ] **Nhập thành công**: `lvt-honor import <file>` báo cáo số hàng.
- [ ] **Nhật ký sạch**: `docker logs <container>` không hiển thị dòng `ERROR` hoặc `CRITICAL`.
- [ ] **Cơ sở dữ liệu có thể truy cập được**: `sqlite3 data/honor.db ".tables"` liệt kê lược đồ.

## Phản ứng sự cố

| Triệu chứng | Chẩn đoán | Cách khắc phục |
|------------|----------|---------|
| `/health` trả về 500 | Cấu hình không hợp lệ hoặc cơ sở dữ liệu bị hỏng. | Kiểm tra nhật ký; đối chiếu `honor.config.json` với schema. Khôi phục cơ sở dữ liệu từ bản sao lưu nếu cần. |
| Đăng nhập quản trị bị lặp (mật khẩu luôn báo sai) | `ADMIN_PASSWORD` chưa được đặt hoặc bị gõ sai trong biến môi trường. | Kiểm tra để biến môi trường khớp chính xác với mật khẩu của bạn. |
| Nhập dữ liệu báo "không tìm thấy cột" | Tiêu đề cột trong CSV không khớp với `data_mapping` trong cấu hình. | Kiểm tra tên cột trong CSV và cập nhật lại `data_mapping` trong cấu hình. |
| Tìm kiếm không ra kết quả dù học sinh có tồn tại | Bộ lọc quá hẹp; hãy thử đặt lại bằng nút **Đặt lại**. | Hoặc tên học sinh đã bị nhập sai chính tả; dùng bảng điều khiển quản trị để kiểm tra lại dữ liệu. |
| Hết dung lượng đĩa | Cơ sở dữ liệu SQLite đã phình quá lớn, hoặc các tệp tạm đang dồn lại. | Lưu trữ dữ liệu cũ, xóa các tệp tạm hoặc nâng cấp dung lượng lưu trữ. |

## Mở rộng

- **Triển khai trên một máy đơn**: `WEB_CONCURRENCY=1`, tệp SQLite trên đĩa cục bộ. Phù hợp với tối đa khoảng 50.000 học sinh.
- **Nhiều worker**: chuyển sang PostgreSQL, đặt `WEB_CONCURRENCY=4` trở lên. Phù hợp với mọi quy mô.

Công cụ truy vấn bị giới hạn bởi I/O chứ không phải CPU. Việc thêm nhân CPU chỉ có ích khi cơ sở dữ liệu nằm ở xa và bị giới hạn bởi độ trễ. Với hầu hết các bản triển khai, một worker duy nhất kèm bộ lưu trữ cục bộ tốc độ cao là đã đủ.

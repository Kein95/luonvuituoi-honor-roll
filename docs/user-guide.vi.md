# Hướng dẫn sử dụng

Hướng dẫn cách dùng cổng thông tin bảng vinh danh: duyệt thư viện, tìm kiếm học sinh, xem hall of fame và quản lý các đội. Nếu bạn là nhà phát triển muốn triển khai cổng thông tin, hãy bắt đầu từ [quickstart.md](quickstart.md).

## Tài liệu này dành cho ai

- **Khách truy cập** (học sinh, phụ huynh, nhà tuyển dụng tiềm năng): xem phần "Duyệt bảng vinh danh".
- **Người vận hành** (cán bộ tổ chức cuộc thi, quản trị viên đào tạo): xem phần "Bảng điều khiển quản trị".

## Duyệt bảng vinh danh

URL: `https://<your-portal>/`

### Lọc theo cuộc thi, năm, huy chương và môn học

Theo mặc định, bảng vinh danh hiển thị tất cả thành tích. Hãy dùng các menu thả xuống để thu hẹp phạm vi hiển thị:

1. **Cuộc thi**: chọn cuộc thi muốn xem.
2. **Năm**: chọn năm hoặc mùa giải.
3. **Huy chương**: lọc theo cấp giải thưởng (Vàng, Bạc, Đồng, Khuyến khích hoặc các cấp tùy chỉnh).
4. **Môn học**: nếu cuộc thi có phân theo môn (TOÁN, TIẾNG ANH, v.v.), hãy lọc theo môn.

Nhấp **Đặt lại** để xóa toàn bộ bộ lọc và hiển thị lại tất cả bản ghi.

### Bố cục hiển thị

Thiết lập `display.layout` quyết định cách hiển thị kết quả:

- **Thẻ**: chế độ xem dạng thư viện, kèm ảnh, tên, trường học, thứ hạng và huy chương của học sinh.
- **Bảng**: chế độ xem dạng bảng dày đặc, hiển thị toàn bộ các cột cùng lúc.
- **Cả hai**: có các tab để chuyển qua lại giữa hai chế độ xem.

## Trang tìm kiếm

URL: `https://<your-portal>/search`

Tìm học sinh theo tên với cơ chế so khớp không phân biệt dấu. Công cụ tìm kiếm:

- Bỏ qua dấu phụ (`Nguyễn` khớp với `Nguyen`).
- Tìm theo cả tên và họ.
- Trả về mọi kết quả khớp trên tất cả cuộc thi và mọi năm.

Tính năng này hữu ích cho khách truy cập muốn tìm một học sinh cụ thể, hoặc xác nhận tên của mình có trong danh sách.

## Danh sách vinh danh

URL: `https://<your-portal>/hall-of-fame`

Bảng xếp hạng danh giá dành cho những cá nhân đạt thành tích cao nhất. Danh sách hiển thị:

- Học sinh sở hữu huy chương danh giá nhất (sắp xếp theo hạng huy chương, sau đó theo mức độ uy tín của cuộc thi).
- Một chế độ xem tùy chọn "nhà vô địch mọi thời đại" hoặc "thành tích trọn đời", nếu cấu hình của bạn có khai báo.
- Huy hiệu trường học và cuộc thi.

Tiêu chí cụ thể phụ thuộc vào phần cấu hình `hall_of_fame` của bạn (sẽ được cải tiến trong tương lai).

## Trang đội

URL: `https://<your-portal>/teams`

Nếu `team_awards` được khai báo trong `honor.config.json`, trang này sẽ hiển thị các giải thưởng dành cho nhóm hoặc tập thể:

- Tên đội và ảnh (nếu có).
- Cấp giải thưởng (Vô địch, Á quân, Đội xuất sắc nhất, v.v.).
- Danh sách thành viên (nếu có trong dữ liệu nhập).
- Liên kết tới trường học.

## Bảng điều khiển quản trị

URL: `https://<your-portal>/admin`

Việc truy cập yêu cầu mật khẩu. Khu vực quản trị cho phép bạn:

- **Thêm thành tích**: tải lên tệp CSV/Excel/JSON để nhập các bản ghi học sinh mới.
- **Xóa thành tích**: loại bỏ những mục nhập sai.
- **Xem số liệu thống kê**: tổng số học sinh, số huy chương theo từng cấp, theo cuộc thi và theo năm.
- **Quản lý cấu hình**: chỉnh sửa `honor.config.json` qua giao diện web (dự kiến; hiện tại thực hiện qua CLI).

### Đăng nhập

1. Truy cập `/login`.
2. Nhập mật khẩu quản trị (cấu hình qua biến môi trường `ADMIN_PASSWORD`).
3. Nhấp **Đăng nhập**. Phiên có hiệu lực trong tab trình duyệt; đóng tab sẽ tự động đăng xuất.

### Thêm thành tích

1. Vào **Quản trị** > **Nhập dữ liệu**.
2. Tải lên một tệp CSV hoặc Excel chứa các bản ghi học sinh.
3. Chỉ định cuộc thi và năm.
4. Chọn **Append** (thêm hàng mới) hoặc **Replace** (xóa dữ liệu của năm trước rồi nhập lại).
5. Xem lại bản tóm tắt sau khi nhập: số hàng đã nhập và các lỗi xác thực.

Quá trình nhập dùng `data_mapping` trong cấu hình để khớp với tiêu đề cột. Nếu thiếu cột hoặc đặt sai tên cột, quá trình nhập sẽ báo lỗi.

### Xóa một thành tích

1. Tìm học sinh bằng bộ lọc cuộc thi, năm, huy chương hoặc môn học.
2. Xác định đúng hàng trong kết quả.
3. Nhấp nút **Xóa**.
4. Xác nhận thao tác xóa.

Hàng sẽ bị xóa ngay lập tức; tệp nhập gốc không bị ảnh hưởng.

### Xem số liệu thống kê

Vào **Quản trị** > **Số liệu thống kê** để xem:

- Tổng số học sinh (không trùng lặp).
- Phân bố huy chương (số lượng Vàng, Bạc, Đồng).
- Các cuộc thi đã công bố.
- Các năm đã có dữ liệu.

## Khắc phục sự cố

| Vấn đề | Giải pháp |
|--------|----------|
| "Không tìm thấy học sinh" nhưng tôi vẫn thấy họ ở nơi khác | Kiểm tra lại các bộ lọc đang đặt (cuộc thi, năm, môn học). Trang tìm kiếm tra trên toàn bộ bản ghi, còn trang chủ chỉ lọc theo lựa chọn hiện tại của bạn. |
| Tìm kiếm quá khắt khe | Tìm kiếm bỏ qua dấu phụ; `Nguyễn` và `Nguyen` là tương đương. Hãy kiểm tra chính tả; tên lót cũng có thể gây sai lệch. |
| Thiếu nút quản trị | Khu vực quản trị đang bị tắt (`admin.enabled: false`). Hãy liên hệ người vận hành trang web. |
| Không đăng nhập được vào trang quản trị | Kiểm tra lại mật khẩu cho đúng. Mật khẩu quản trị được đặt qua `ADMIN_PASSWORD` tại thời điểm triển khai, không nằm trong cấu hình. |
| Nhập dữ liệu thất bại với lỗi "không tìm thấy cột" | Kiểm tra xem tiêu đề trong tệp CSV có khớp với `data_mapping` trong `honor.config.json` hay không. |

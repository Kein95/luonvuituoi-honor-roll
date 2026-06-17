# Hướng dẫn sử dụng

Cách sử dụng cổng thông tin bảng vinh danh: duyệt thư viện, tìm kiếm học sinh, xem hall of fame và quản lý các đội. Nếu bạn là nhà phát triển triển khai cổng thông tin, hãy bắt đầu từ [quickstart.md](quickstart.md) thay thế.

## Ai đọc cái này

- **Khách truy cập** (học sinh, phụ huynh, nhà tuyển dụng tiềm năng): xem phần "Duyệt bảng vinh danh".
- **Nhà điều hành** (nhân viên cuộc thi, quản trị viên đào tạo): xem phần "Bảng điều khiển quản trị".

## Duyệt bảng vinh danh

URL: `https://<your-portal>/`

### Lọc theo cuộc thi, năm, huy chương và môn học

Bảng vinh danh hiển thị tất cả các thành tích theo mặc định. Sử dụng các menu thả xuống bộ lọc để thu hẹp chế độ xem:

1. **Cuộc thi**: chọn cuộc thi hay cuộc đua nào để xem.
2. **Năm**: chọn năm/mùa.
3. **Huy chương**: lọc theo cấp độ giải thưởng (Vàng, Bạc, Đồng, Công lao hoặc các cấp tùy chỉnh).
4. **Môn học**: nếu cuộc thi theo dõi các môn học (TOÁN, TIẾNG ANH, v.v.), hãy lọc theo môn.

Nhấp **Đặt lại** để xóa tất cả các bộ lọc và hiển thị tất cả các bản ghi.

### Bố cục xem

Cài đặt `display.layout` kiểm soát cách kết quả được hiển thị:

- **Thẻ**: chế độ xem thư viện với ảnh, tên, trường học, xếp hạng và huy chương của học sinh.
- **Bảng**: chế độ xem bảng dày đặc hiển thị tất cả các cột cùng một lúc.
- **Cả hai**: các tab để chuyển đổi giữa hai chế độ xem.

## Trang tìm kiếm

URL: `https://<your-portal>/search`

Tìm học sinh theo tên bằng cách so khớp dung thích dấu. Công cụ tìm kiếm:

- Loại bỏ dấu phụ (`Nguyễn` phù hợp với `Nguyen`).
- Tìm kiếm tên + họ.
- Trả về tất cả các trận đấu trên tất cả các cuộc thi và năm.

Hữu ích cho những khách truy cập muốn tìm một học sinh cụ thể hoặc xác minh tên của họ xuất hiện trong danh sách.

## Danh sách vinh danh

URL: `https://<your-portal>/hall-of-fame`

Bảng xếp hạng uy tín của những người đạt thành tích hàng đầu. Danh sách hiển thị:

- Học sinh có huy chương uy tín nhất (được sắp xếp theo xếp hạng huy chương, sau đó theo tính nổi bật của cuộc thi).
- Một chế độ xem "nhà vô địch mọi thời đại" hoặc "thành tích trọn đời" tùy chọn nếu cấu hình của bạn xác định nó.
- Huy hiệu trường học và cuộc thi.

Tiêu chí chính xác phụ thuộc vào phần cấu hình `hall_of_fame` của bạn (cải tiến trong tương lai).

## Trang đội

URL: `https://<your-portal>/teams`

Nếu `team_awards` được cấu hình trong `honor.config.json` của bạn, trang này hiển thị các khen thưởng nhóm/tập thể:

- Tên đội và ảnh (nếu được cung cấp).
- Cấp độ giải thưởng (Nhà vô địch, Runner-up, Đội giỏi nhất, v.v.).
- Danh sách thành viên (nếu có trong dữ liệu nhập).
- Liên kết trường học.

## Bảng điều khiển quản trị

URL: `https://<your-portal>/admin`

Truy cập yêu cầu mật khẩu. Bề mặt quản trị cho phép bạn:

- **Thêm thành tích**: tải lên tệp CSV/Excel/JSON để nhập các bản ghi học sinh mới.
- **Xóa thành tích**: loại bỏ các mục nhập không chính xác.
- **Xem số liệu thống kê**: tổng số học sinh, huy chương trên từng cấp, cuộc thi, năm.
- **Quản lý cấu hình**: chỉnh sửa `honor.config.json` qua giao diện web (dự kiến; hiện tại qua CLI).

### Đăng nhập

1. Điều hướng đến `/login`.
2. Nhập mật khẩu quản trị (đặt thông qua biến môi trường `ADMIN_PASSWORD`).
3. Nhấp **Đăng nhập**. Phiên của bạn có giá trị cho tab trình duyệt; đóng nó sẽ đăng xuất bạn.

### Thêm thành tích

1. Đi tới **Quản trị** > **Nhập dữ liệu**.
2. Tải lên một tệp CSV hoặc Excel với các bản ghi học sinh.
3. Chỉ định cuộc thi và năm.
4. Chọn **Append** (thêm hàng mới) hoặc **Replace** (xóa dữ liệu của năm trước).
5. Xem lại tóm tắt nhập: số hàng được nhập, lỗi xác thực.

Nhập sử dụng `data_mapping` trong cấu hình của bạn để phù hợp với tiêu đề cột. Nếu cột bị thiếu hoặc đặt tên sai, nhập sẽ báo cáo lỗi.

### Xóa một thành tích

1. Tìm kiếm học sinh theo bộ lọc cuộc thi, năm, huy chương hoặc môn học.
2. Tìm hàng trong kết quả.
3. Nhấp vào nút **Xóa**.
4. Xác nhận việc xóa.

Hàng bị xóa ngay lập tức; tệp nhập gốc không bị ảnh hưởng.

### Xem số liệu thống kê

Điều hướng đến **Quản trị** > **Số liệu thống kê** để xem:

- Tổng số học sinh độc nhất.
- Phân phối huy chương (có bao nhiêu Vàng, Bạc, Đồng).
- Cuộc thi được công bố.
- Năm có dữ liệu.

## Khắc phục sự cố

| Vấn đề | Giải pháp |
|--------|----------|
| "Học sinh không tìm thấy" nhưng tôi nhìn thấy họ ở nơi khác | Kiểm tra cài đặt bộ lọc (cuộc thi, năm, môn học). Trang tìm kiếm tìm kiếm trên tất cả các bản ghi; trang chủ lọc theo lựa chọn hiện tại của bạn. |
| Tìm kiếm quá nghiêm ngặt | Tìm kiếm loại bỏ dấu phụ; `Nguyễn` và `Nguyen` tương đương. Kiểm tra chính tả; tên lót có vấn đề. |
| Nút quản trị bị thiếu | Bề mặt quản trị bị tắt (`admin.enabled: false`). Liên hệ với nhà điều hành trang web. |
| Không thể đăng nhập vào quản trị | Xác minh mật khẩu là chính xác. Mật khẩu quản trị được đặt thông qua `ADMIN_PASSWORD` tại thời điểm triển khai, không có trong cấu hình. |
| Nhập không thành công với "cột không tìm thấy" | Kiểm tra tiêu đề CSV của bạn khớp với `data_mapping` trong `honor.config.json` của bạn. |

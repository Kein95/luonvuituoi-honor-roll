# Khắc phục sự cố

Các vấn đề phổ biến và giải pháp khi thiết lập, chạy hoặc sử dụng LUONVUITUOI-HONOR ROLL.

## Cài đặt và thiết lập

### Lệnh `lvt-honor` không tìm thấy

**Triệu chứng:** Chạy `lvt-honor init` trả về `command not found`.

**Nguyên nhân:** Gói CLI không được cài đặt hoặc không có trong PATH của bạn.

**Sửa chữa:**

```bash
# Cài đặt CLI từ PyPI
pip install luonvuitoi-honor-cli

# Hoặc từ sao chép dev cục bộ
cd packages/cli && pip install -e .

# Xác minh
lvt-honor --version
```

### Không khớp phiên bản Python

**Triệu chứng:** `lvt-honor` không thành công với `SyntaxError` hoặc `TypeError` về gợi ý kiểu.

**Nguyên nhân:** Bạn đang chạy Python < 3.10. Dự án yêu cầu Python 3.10+.

**Sửa chữa:**

```bash
python3 --version
# Nếu < 3.10, nâng cấp hoặc sử dụng trình quản lý phiên bản (pyenv, asdf)
pyenv install 3.12
pyenv local 3.12
```

### Xác thực cấu hình không thành công khi tải

**Triệu chứng:** `lvt-honor dev` trả về `ValidationError: ...` và sẽ không khởi động.

**Nguyên nhân:** `honor.config.json` của bạn có lỗi đánh máy hoặc cấu trúc không hợp lệ.

**Sửa chữa:**

1. Mở `honor.config.json` trong trình soạn thảo JSON (VS Code, Sublime, v.v.).
2. Kiểm tra các lỗi phổ biến:
   - Dấu phẩy sau cùng trong mảng hoặc đối tượng.
   - Các trường bắt buộc bị thiếu (`project`, `competitions`, `editions`, `medals`).
   - Mã huy chương trong `competitions[].medals` không tồn tại trong sổ đăng ký huy chương cấp cao nhất `medals`.
   - `edition.competition_id` tham chiếu đến một cuộc thi không tồn tại.
3. Xác thực lại lược đồ:

```bash
# Tải xuống lược đồ
curl -o honor.schema.json https://raw.githubusercontent.com/Kein95/luonvuituoi-honor-roll/main/honor.schema.json

# Xác thực (yêu cầu ajv-cli)
npm install -g ajv-cli
ajv validate -s honor.schema.json -d honor.config.json
```

## Chạy cục bộ

### Cổng đã được sử dụng

**Triệu chứng:** `lvt-honor dev` không thành công với `Address already in use: ('127.0.0.1', 8000)`.

**Nguyên nhân:** Một quy trình khác đang lắng nghe cổng 8000.

**Sửa chữa:**

```bash
# Tìm những gì đang sử dụng cổng 8000
lsof -i :8000
# Giết nó
kill -9 <PID>

# Hoặc sử dụng một cổng khác
lvt-honor dev --port 9000
```

### Cơ sở dữ liệu bị khóa

**Triệu chứng:** Nhập dữ liệu hoặc xem trang trả về `database is locked`.

**Nguyên nhân:** Một quy trình khác (một phiên bản `lvt-honor` khác hoặc một quy trình Python bị bỏ đi) có khóa độc quyền trên cơ sở dữ liệu.

**Sửa chữa:**

```bash
# Giết bất kỳ quy trình Python lạc nào
pkill -f "lvt-honor dev"

# Hoặc trên Windows
taskkill /F /IM python.exe

# Thử lại
lvt-honor dev
```

### Nhập không thành công với "cột không tìm thấy"

**Triệu chứng:** `lvt-honor import results.csv` trả về `KeyError: 'expected_column_name'`.

**Nguyên nhân:** Tiêu đề CSV của bạn không khớp với `data_mapping` trong cấu hình của bạn.

**Sửa chữa:**

1. Kiểm tra tiêu đề CSV:

```bash
head -1 results.csv
# Đầu ra: sbd, name, school, subject, medal, rank
```

2. Kiểm tra cấu hình:

```bash
grep -A 10 '"data_mapping"' honor.config.json
```

3. Nếu tiêu đề không khớp, hãy:
   - **Đổi tên các cột CSV** để khớp với cấu hình, HOẶC
   - **Cập nhật `data_mapping`** trong cấu hình để khớp với CSV.

Ví dụ:

```json
"data_mapping": {
  "candidate_no_col": "sbd",
  "name_col": "name",
  "school_col": "school",
  "subject_col": "subject",
  "medal_col": "medal",
  "rank_col": "rank"
}
```

## Duyệt cổng thông tin

### Tìm kiếm không trả về kết quả, nhưng tôi thấy học sinh ở nơi khác

**Nguyên nhân:** Tìm kiếm đang hoạt động, nhưng tên học sinh không được nhập hoặc được nhập với cách viết khác.

**Sửa chữa:**

1. Kiểm tra các bộ lọc trên trang chủ — chúng có thể làm hẹp chế độ xem.
2. Sử dụng bảng điều khiển quản trị để xác minh học sinh có trong cơ sở dữ liệu:

```bash
sqlite3 data/honor.db "SELECT name, school, medal FROM achievements WHERE name LIKE '%nguyen%' LIMIT 5;"
```

3. Nếu học sinh có trong cơ sở dữ liệu nhưng tìm kiếm không tìm thấy họ, hãy kiểm tra mã hóa tên (UTF-8 vs. Latin-1).

### Bộ lọc không làm hẹp kết quả

**Nguyên nhân:** Bạn đã chọn bộ lọc, nhưng trang vẫn hiển thị tất cả học sinh.

**Sửa chữa:**

1. Làm mới trang.
2. Kiểm tra rằng giá trị bộ lọc tồn tại trong dữ liệu:

```bash
# Kiểm tra xem cuộc thi có tồn tại không
sqlite3 data/honor.db "SELECT DISTINCT competition_id FROM achievements;"

# Kiểm tra nếu năm có dữ liệu
sqlite3 data/honor.db "SELECT DISTINCT year FROM achievements WHERE competition_id = 'demo-a';"
```

### Ảnh bị hỏng (404 hoặc trống)

**Nguyên nhân:** URL ảnh trong dữ liệu nhập bị thiếu hoặc không chính xác.

**Sửa chữa:**

1. Kiểm tra `data_mapping` trong cấu hình — `photo_col` sẽ chỉ đến cột CSV chính xác.
2. Xác minh URL ảnh là tuyệt đối (bắt đầu bằng `http://`, `https://` hoặc `data:image/`).
3. Kiểm tra rằng các URL vẫn hợp lệ:

```bash
curl -I "https://example.com/student-photo.jpg"
# Nên trả về 200, không phải 404
```

4. Nếu ảnh là tùy chọn, hãy đặt `photo_col: null` trong cấu hình:

```json
"data_mapping": { "photo_col": null }
```

## Bảng điều khiển quản trị

### Nút quản trị bị thiếu

**Nguyên nhân:** Bề mặt quản trị bị tắt (`admin.enabled: false`).

**Sửa chữa:**

Chỉnh sửa `honor.config.json` và đặt:

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

Sau đó khởi động lại cổng thông tin.

### Không thể đăng nhập (mật khẩu luôn sai)

**Nguyên nhân:** Biến môi trường `ADMIN_PASSWORD` không được đặt hoặc không chính xác.

**Sửa chữa:**

```bash
# Kiểm tra xem biến có được đặt không
echo $ADMIN_PASSWORD

# Nếu trống, hãy đặt nó
export ADMIN_PASSWORD="your-secure-password"

# Khởi động lại
lvt-honor dev
```

### Đăng nhập hoạt động, nhưng trang quản trị trống hoặc bị hỏng

**Nguyên nhân:** Lỗi JavaScript hoặc vấn đề cookie phiên.

**Sửa chữa:**

1. Mở DevTools trình duyệt (F12) và kiểm tra Console để tìm lỗi.
2. Kiểm tra tab Network — các yêu cầu đến `/api/admin/*` có trả về 200 không?
3. Thử xóa cookie và đăng nhập lại:

```bash
# Trong bảng điều khiển trình duyệt
document.cookie.split(";").forEach(c => {
  const eqPos = c.indexOf("=");
  const name = eqPos > -1 ? c.substr(0, eqPos).trim() : c.trim();
  document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
});
```

Sau đó tải lại trang và đăng nhập lại.

## Triển khai Docker

### Vùng chứa thoát ngay lập tức

**Triệu chứng:** `docker compose up` cho thấy vùng chứa thoát với mã 1.

**Sửa chữa:**

```bash
# Kiểm tra nhật ký
docker compose logs honor

# Các nguyên nhân phổ biến:
# - ADMIN_PASSWORD không được đặt trong .env
# - honor.config.json không hợp lệ
# - thư mục project/data/ bị thiếu

# Xác minh
ls -la project/honor.config.json
grep ADMIN_PASSWORD .env
```

### `Permission denied` khi gắn dự án

**Triệu chứng:** Vùng chứa chạy nhưng không thể đọc `project/honor.config.json`.

**Sửa chữa:**

```bash
# Đảm bảo thư mục dự án có thể đọc được
chmod 755 project/
chmod 644 project/honor.config.json

# Khởi động lại
docker compose restart
```

### Cơ sở dữ liệu bị khóa trong Docker

**Nguyên nhân:** Nhiều quy trình worker đua tranh trên SQLite (phổ biến với `WEB_CONCURRENCY > 1`).

**Sửa chữa:**

Trong `docker-compose.yml`, hãy đảm bảo:

```yaml
environment:
  WEB_CONCURRENCY: 1
```

Nếu bạn cần mở rộng, hãy di chuyển đến PostgreSQL.

## Triển khai Vercel

### Xây dựng không thành công: `ModuleNotFoundError`

**Triệu chứng:** Nhật ký xây dựng Vercel cho thấy `ModuleNotFoundError: No module named 'luonvuitoi_honor'`.

**Nguyên nhân:** Các phụ thuộc không được cài đặt trong quá trình xây dựng.

**Sửa chữa:**

Đảm bảo `requirements.txt` của bạn (hoặc `pyproject.toml` với `poetry install`) nằm trong thư mục gốc dự án:

```bash
cat requirements.txt
# Nên liệt kê: luonvuitoi-honor-cli, ...

# Nếu thiếu, hãy tạo nó
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: add requirements.txt"
git push
```

### Bề mặt quản trị trả về 401

**Triệu chứng:** Đăng nhập vào `/admin` trên Vercel luôn trả về 401.

**Nguyên nhân:** `ADMIN_PASSWORD` không được đặt trong các biến môi trường Vercel.

**Sửa chữa:**

1. Đi tới **Settings** > **Environment Variables** trong bảng điều khiển Vercel.
2. Thêm `ADMIN_PASSWORD` với mật khẩu an toàn của bạn.
3. Triển khai lại.

### Cold start chậm

**Triệu chứng:** Yêu cầu đầu tiên mất 3–5 giây.

**Nguyên nhân:** Cold start serverless là bình thường. Khởi tạo thời gian chạy Python mất ~ 200ms, cộng với nhập.

**Giảm nhẹ:**

- Sử dụng tính năng **Concurrency** của Vercel để giữ hàm ấm.
- Hãy xem xét sử dụng lưu trữ thường trực hơn (Docker trên Railway, Render, v.v.).

## Gỡ lỗi chung

### Bật ghi nhật ký gỡ lỗi

```bash
# Đặt mức nhật ký
export LOG_LEVEL=DEBUG
lvt-honor dev
```

### Kiểm tra cơ sở dữ liệu

```bash
# Mở CLI SQLite
sqlite3 data/honor.db

# Liệt kê bảng
.tables

# Hiển thị lược đồ
.schema achievements

# Đếm hàng
SELECT COUNT(*) FROM achievements;

# Tìm các vấn đề dữ liệu
SELECT * FROM achievements WHERE name LIKE '%unknown%' LIMIT 5;
```

### Kiểm tra các biến môi trường

```bash
# Liệt kê tất cả các biến env mà ứng dụng nhìn thấy
env | grep -E "ADMIN|SECRET|PUBLIC"

# Kiểm tra một biến cụ thể
echo $ADMIN_PASSWORD
```

## Vẫn còn bị mắc kẹt?

Nếu không có giải pháp nào hoạt động:

1. **Kiểm tra nhật ký** — cả nhật ký ứng dụng và nhật ký hệ thống (`docker logs`, `vercel logs --follow`).
2. **Đọc thông báo lỗi cẩn thận** — nó thường gợi ý nguyên nhân gốc.
3. **Cô lập vấn đề** — đó là trong quá trình thiết lập, nhập, duyệt hay triển khai?
4. **Tìm kiếm các vấn đề GitHub** — vấn đề của bạn có thể được ghi lại.
5. **Yêu cầu trợ giúp** — mở Thảo luận hoặc vấn đề GitHub với:
   - Phiên bản Python (`python --version`)
   - Hệ điều hành và môi trường (Docker, Vercel, dev cục bộ)
   - Các bước để tái tạo
   - Thông báo lỗi đầy đủ và nhật ký

# Khắc phục sự cố

Các vấn đề thường gặp và cách xử lý khi cài đặt, chạy hoặc sử dụng LUONVUITUOI-HONOR ROLL.

## Cài đặt và thiết lập

### Không tìm thấy lệnh `lvt-honor`

**Triệu chứng:** Chạy `lvt-honor init` báo `command not found`.

**Nguyên nhân:** Gói CLI chưa được cài đặt hoặc không nằm trong PATH của bạn.

**Cách xử lý:**

```bash
# Cài đặt CLI từ PyPI
pip install luonvuitoi-honor-cli

# Hoặc cài từ bản clone dev cục bộ
cd packages/cli && pip install -e .

# Kiểm tra lại
lvt-honor --version
```

### Sai phiên bản Python

**Triệu chứng:** `lvt-honor` lỗi với `SyntaxError` hoặc `TypeError` liên quan đến gợi ý kiểu (type hint).

**Nguyên nhân:** Bạn đang chạy Python < 3.10. Dự án yêu cầu Python 3.10 trở lên.

**Cách xử lý:**

```bash
python3 --version
# Nếu < 3.10, nâng cấp hoặc sử dụng trình quản lý phiên bản (pyenv, asdf)
pyenv install 3.12
pyenv local 3.12
```

### Xác thực cấu hình thất bại khi khởi động

**Triệu chứng:** `lvt-honor dev` báo `ValidationError: ...` và không khởi động được.

**Nguyên nhân:** Tệp `honor.config.json` của bạn có lỗi đánh máy hoặc cấu trúc không hợp lệ.

**Cách xử lý:**

1. Mở `honor.config.json` bằng một trình soạn thảo JSON (VS Code, Sublime, v.v.).
2. Kiểm tra các lỗi thường gặp:
   - Dấu phẩy thừa ở cuối mảng hoặc đối tượng.
   - Thiếu các trường bắt buộc (`project`, `competitions`, `editions`, `medals`).
   - Mã huy chương trong `competitions[].medals` không có trong sổ đăng ký huy chương cấp cao nhất `medals`.
   - `edition.competition_id` trỏ đến một cuộc thi không tồn tại.
3. Xác thực lại theo lược đồ:

```bash
# Tải lược đồ về
curl -o honor.schema.json https://raw.githubusercontent.com/Kein95/luonvuituoi-honor-roll/main/honor.schema.json

# Xác thực (cần có ajv-cli)
npm install -g ajv-cli
ajv validate -s honor.schema.json -d honor.config.json
```

## Chạy cục bộ

### Cổng đang bị chiếm dụng

**Triệu chứng:** `lvt-honor dev` lỗi với `Address already in use: ('127.0.0.1', 8000)`.

**Nguyên nhân:** Một tiến trình khác đang lắng nghe trên cổng 8000.

**Cách xử lý:**

```bash
# Tìm tiến trình đang chiếm cổng 8000
lsof -i :8000
# Kết thúc tiến trình đó
kill -9 <PID>

# Hoặc chạy trên một cổng khác
lvt-honor dev --port 9000
```

### Cơ sở dữ liệu bị khóa

**Triệu chứng:** Nhập dữ liệu hoặc xem trang đều báo `database is locked`.

**Nguyên nhân:** Một tiến trình khác (một phiên `lvt-honor` khác, hoặc một tiến trình Python còn sót lại) đang giữ khóa độc quyền trên cơ sở dữ liệu.

**Cách xử lý:**

```bash
# Kết thúc mọi tiến trình Python còn sót lại
pkill -f "lvt-honor dev"

# Hoặc trên Windows
taskkill /F /IM python.exe

# Thử lại
lvt-honor dev
```

### Nhập dữ liệu thất bại với lỗi "không tìm thấy cột"

**Triệu chứng:** `lvt-honor import results.csv` báo `KeyError: 'expected_column_name'`.

**Nguyên nhân:** Tiêu đề trong tệp CSV không khớp với `data_mapping` trong cấu hình của bạn.

**Cách xử lý:**

1. Kiểm tra tiêu đề CSV:

```bash
head -1 results.csv
# Đầu ra: sbd, name, school, subject, medal, rank
```

2. Kiểm tra cấu hình:

```bash
grep -A 10 '"data_mapping"' honor.config.json
```

3. Nếu tiêu đề không khớp, hãy chọn một trong hai cách:
   - **Đổi tên các cột trong CSV** cho khớp với cấu hình, HOẶC
   - **Cập nhật `data_mapping`** trong cấu hình cho khớp với CSV.

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

### Tìm kiếm không ra kết quả, nhưng tôi thấy học sinh ở nơi khác

**Nguyên nhân:** Tìm kiếm vẫn hoạt động, nhưng tên học sinh chưa được nhập hoặc đã nhập theo cách viết khác.

**Cách xử lý:**

1. Kiểm tra các bộ lọc trên trang chủ, vì chúng có thể đang thu hẹp phạm vi hiển thị.
2. Dùng bảng điều khiển quản trị để xác nhận học sinh có trong cơ sở dữ liệu:

```bash
sqlite3 data/honor.db "SELECT name, school, medal FROM achievements WHERE name LIKE '%nguyen%' LIMIT 5;"
```

3. Nếu học sinh có trong cơ sở dữ liệu nhưng tìm kiếm không thấy, hãy kiểm tra cách mã hóa tên (UTF-8 hay Latin-1).

### Bộ lọc không thu hẹp kết quả

**Nguyên nhân:** Bạn đã chọn bộ lọc nhưng trang vẫn hiển thị toàn bộ học sinh.

**Cách xử lý:**

1. Tải lại trang.
2. Kiểm tra xem giá trị bộ lọc có tồn tại trong dữ liệu hay không:

```bash
# Kiểm tra cuộc thi có tồn tại không
sqlite3 data/honor.db "SELECT DISTINCT competition_id FROM achievements;"

# Kiểm tra năm có dữ liệu không
sqlite3 data/honor.db "SELECT DISTINCT year FROM achievements WHERE competition_id = 'demo-a';"
```

### Ảnh bị lỗi (404 hoặc trống)

**Nguyên nhân:** URL ảnh trong dữ liệu nhập bị thiếu hoặc sai.

**Cách xử lý:**

1. Kiểm tra `data_mapping` trong cấu hình. Trường `photo_col` phải trỏ đúng cột CSV.
2. Đảm bảo URL ảnh là URL tuyệt đối (bắt đầu bằng `http://`, `https://` hoặc `data:image/`).
3. Kiểm tra xem các URL còn hợp lệ hay không:

```bash
curl -I "https://example.com/student-photo.jpg"
# Phải trả về 200, không phải 404
```

4. Nếu ảnh là tùy chọn, hãy đặt `photo_col: null` trong cấu hình:

```json
"data_mapping": { "photo_col": null }
```

## Bảng điều khiển quản trị

### Thiếu nút quản trị

**Nguyên nhân:** Khu vực quản trị đang bị tắt (`admin.enabled: false`).

**Cách xử lý:**

Sửa `honor.config.json` và đặt:

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

Sau đó khởi động lại cổng thông tin.

### Không đăng nhập được (mật khẩu luôn báo sai)

**Nguyên nhân:** Biến môi trường `ADMIN_PASSWORD` chưa được đặt hoặc bị sai.

**Cách xử lý:**

```bash
# Kiểm tra xem biến đã được đặt chưa
echo $ADMIN_PASSWORD

# Nếu trống, hãy đặt giá trị cho biến
export ADMIN_PASSWORD="your-secure-password"

# Khởi động lại
lvt-honor dev
```

### Đăng nhập được, nhưng trang quản trị trống hoặc bị lỗi

**Nguyên nhân:** Lỗi JavaScript hoặc trục trặc cookie phiên.

**Cách xử lý:**

1. Mở DevTools của trình duyệt (F12) và xem tab Console để tìm lỗi.
2. Kiểm tra tab Network: các yêu cầu đến `/api/admin/*` có trả về 200 không?
3. Thử xóa cookie rồi đăng nhập lại:

```bash
# Trong bảng điều khiển (console) của trình duyệt
document.cookie.split(";").forEach(c => {
  const eqPos = c.indexOf("=");
  const name = eqPos > -1 ? c.substr(0, eqPos).trim() : c.trim();
  document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
});
```

Sau đó tải lại trang và đăng nhập lại.

## Triển khai Docker

### Container thoát ngay lập tức

**Triệu chứng:** `docker compose up` cho thấy container thoát với mã 1.

**Cách xử lý:**

```bash
# Xem nhật ký
docker compose logs honor

# Các nguyên nhân thường gặp:
# - ADMIN_PASSWORD chưa được đặt trong .env
# - honor.config.json không hợp lệ
# - thiếu thư mục project/data/

# Kiểm tra lại
ls -la project/honor.config.json
grep ADMIN_PASSWORD .env
```

### `Permission denied` khi mount thư mục dự án

**Triệu chứng:** Container chạy được nhưng không đọc được `project/honor.config.json`.

**Cách xử lý:**

```bash
# Đảm bảo thư mục dự án có quyền đọc
chmod 755 project/
chmod 644 project/honor.config.json

# Khởi động lại
docker compose restart
```

### Cơ sở dữ liệu bị khóa trong Docker

**Nguyên nhân:** Nhiều tiến trình worker tranh chấp trên SQLite (thường xảy ra khi `WEB_CONCURRENCY > 1`).

**Cách xử lý:**

Trong `docker-compose.yml`, hãy đảm bảo:

```yaml
environment:
  WEB_CONCURRENCY: 1
```

Nếu cần mở rộng quy mô, hãy chuyển sang PostgreSQL.

## Triển khai Vercel

### Build thất bại: `ModuleNotFoundError`

**Triệu chứng:** Nhật ký build trên Vercel hiển thị `ModuleNotFoundError: No module named 'luonvuitoi_honor'`.

**Nguyên nhân:** Các phụ thuộc không được cài đặt trong quá trình build.

**Cách xử lý:**

Đảm bảo tệp `requirements.txt` (hoặc `pyproject.toml` dùng với `poetry install`) nằm ở thư mục gốc của dự án:

```bash
cat requirements.txt
# Phải liệt kê: luonvuitoi-honor-cli, ...

# Nếu thiếu, hãy tạo tệp này
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: add requirements.txt"
git push
```

### Khu vực quản trị trả về 401

**Triệu chứng:** Đăng nhập vào `/admin` trên Vercel luôn trả về 401.

**Nguyên nhân:** `ADMIN_PASSWORD` chưa được đặt trong biến môi trường của Vercel.

**Cách xử lý:**

1. Vào **Settings** > **Environment Variables** trong bảng điều khiển Vercel.
2. Thêm `ADMIN_PASSWORD` cùng mật khẩu an toàn của bạn.
3. Triển khai lại.

### Cold start chậm

**Triệu chứng:** Yêu cầu đầu tiên mất 3-5 giây.

**Nguyên nhân:** Cold start là điều bình thường với serverless. Việc khởi tạo môi trường chạy Python mất khoảng 200ms, cộng thêm thời gian import.

**Cách giảm thiểu:**

- Dùng tính năng **Concurrency** của Vercel để giữ hàm luôn ở trạng thái nóng (warm).
- Cân nhắc dùng hình thức lưu trữ thường trực hơn (Docker trên Railway, Render, v.v.).

## Gỡ lỗi chung

### Bật ghi nhật ký ở mức gỡ lỗi

```bash
# Đặt mức nhật ký
export LOG_LEVEL=DEBUG
lvt-honor dev
```

### Kiểm tra cơ sở dữ liệu

```bash
# Mở CLI SQLite
sqlite3 data/honor.db

# Liệt kê các bảng
.tables

# Hiển thị lược đồ
.schema achievements

# Đếm số hàng
SELECT COUNT(*) FROM achievements;

# Tìm các vấn đề về dữ liệu
SELECT * FROM achievements WHERE name LIKE '%unknown%' LIMIT 5;
```

### Kiểm tra các biến môi trường

```bash
# Liệt kê tất cả biến môi trường mà ứng dụng nhìn thấy
env | grep -E "ADMIN|SECRET|PUBLIC"

# Kiểm tra một biến cụ thể
echo $ADMIN_PASSWORD
```

## Vẫn chưa khắc phục được?

Nếu không cách nào ở trên hiệu quả:

1. **Xem nhật ký**: kiểm tra cả nhật ký ứng dụng lẫn nhật ký hệ thống (`docker logs`, `vercel logs --follow`).
2. **Đọc kỹ thông báo lỗi**: thông báo này thường gợi ý nguyên nhân gốc rễ.
3. **Khoanh vùng vấn đề**: lỗi nằm ở khâu thiết lập, nhập liệu, duyệt trang hay triển khai?
4. **Tìm trong các issue trên GitHub**: vấn đề của bạn có thể đã được ghi nhận.
5. **Nhờ hỗ trợ**: tạo một Discussion hoặc issue trên GitHub, kèm theo:
   - Phiên bản Python (`python --version`)
   - Hệ điều hành và môi trường (Docker, Vercel, dev cục bộ)
   - Các bước để tái hiện lỗi
   - Toàn bộ thông báo lỗi và nhật ký

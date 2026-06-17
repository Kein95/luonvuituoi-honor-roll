# Tài liệu tham khảo cấu hình

`honor.config.json` định nghĩa toàn bộ cổng thông tin. Mọi khóa đều được xác thực bằng các mô hình Pydantic (`extra="forbid"`), nên lỗi gõ sai sẽ báo lỗi ngay khi tải. Tệp [`honor.schema.json`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/honor.schema.json) đi kèm trong kho cung cấp gợi ý tự động cho trình soạn thảo. Hãy trỏ tệp cấu hình của bạn tới schema này:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Kein95/luonvuituoi-honor-roll/main/honor.schema.json",
  "project": { /* … */ }
}
```

## Khóa cấp cao nhất

| Khóa | Loại | Bắt buộc | Mô tả |
|------|------|---------|-------|
| `project` | object | ✓ | Tên hiển thị, slug, locale, khẩu hiệu, thương hiệu. |
| `competitions` | array | ✓ (≥1) | Các cuộc thi bạn công bố (Demo Olympiad A, Demo Olympiad B, …). |
| `editions` | array | ✓ (≥1) | Các cặp cuộc thi và năm mà bạn đã tổ chức. |
| `medals` | object | ✓ (≥1) | Sổ đăng ký huy chương toàn cục: mã → định nghĩa. |
| `data_mapping` | object | | Ánh xạ tên cột khi nhập dữ liệu. |
| `display` | object | | Bố cục giao diện và giá trị mặc định. |
| `admin` | object | | Công tắc bật/tắt bề mặt quản trị và chế độ xác thực. |

## `project`

```json
"project": {
  "name": "LUONVUITUOI HONOR ROLL",
  "slug": "demo-honor",
  "locale": "vi",
  "tagline": "Vinh danh học sinh Việt Nam",
  "branding": { "primary_color": "#667eea", "accent_color": "#764ba2", "logo_url": null }
}
```

- `slug` phải là kebab-case chữ thường; giá trị này dùng để đặt tên tệp SQLite (`data/<slug>.db`).
- `locale` nhận giá trị `"en"` hoặc `"vi"`, quyết định bộ chuỗi giao diện hiển thị.
- `branding.logo_url` phải bắt đầu bằng `/`, `http://`, `https://` hoặc `data:image/` (nhằm chặn đường rò rỉ qua XSS).

## `competitions[]`

```json
{
  "id": "demo-a",
  "name": "Demo Olympiad A",
  "name_vi": "Demo Olympiad A",
  "candidate_field": "sbd",
  "subjects": [
    { "code": "MATH", "name": "Mathematics", "name_vi": "Toán học" }
  ],
  "medals": ["GOLD", "SILVER", "BRONZE", "MERIT"]
}
```

- `id` là một mã định danh an toàn cho URL theo dạng `[A-Za-z0-9_-]+`.
- `medals` được chuyển thành chữ hoa và loại bỏ trùng lặp khi tải; mỗi mục **phải** tồn tại trong sổ đăng ký `medals` ở cấp cao nhất (kiểm tra liên trường).

## `editions[]`

```json
{ "competition_id": "demo-a", "year": 2025, "label": "Demo Olympiad A 2025" }
```

- `competition_id` phải tham chiếu một cuộc thi đã được khai báo (kiểm tra liên trường).
- Các cặp `(competition_id, year)` phải là duy nhất: mỗi cuộc thi trong mỗi năm chỉ có một phiên bản.

## `medals`

```json
"medals": {
  "GOLD":   { "rank": 1, "label_en": "Gold Medal",   "label_vi": "Huy chương Vàng", "color": "#FFD700", "icon": "🥇" },
  "SILVER": { "rank": 2, "label_en": "Silver Medal", "label_vi": "Huy chương Bạc",  "color": "#C0C0C0", "icon": "🥈" }
}
```

- `rank` quyết định thứ tự sắp xếp (giá trị càng thấp thì càng danh giá; thứ hạng phải là duy nhất).
- `color` là chuỗi mã hex dùng làm màu nền cho huy hiệu huy chương.

## `data_mapping`

Ánh xạ các tiêu đề cột trong tệp nguồn của bạn sang các trường logic. Theo mặc định, hệ thống giả định có các cột `candidate_no`, `name`, `grade`, `photo`, `school`, `rank`, `medal`, `subject`. Trường `photo` là một URL (https, đường dẫn tương đối trong site dạng `/path`, hoặc URI `data:`) được hiển thị làm ảnh đại diện của học sinh:

```json
"data_mapping": {
  "candidate_no_col": "candidate_no",
  "name_col": "name",
  "grade_col": "grade",
  "photo_col": "photo",
  "school_col": "school",
  "rank_col": "rank",
  "medal_col": "medal",
  "subject_col": "subject",
  "percentile_col": null
}
```

Với bất kỳ cột tùy chọn nào mà nguồn dữ liệu của bạn không có, hãy đặt giá trị `null` hoặc bỏ qua cột đó.

## `display`

```json
"display": {
  "layout": "both",
  "show_rank": true,
  "show_percentile": false,
  "cards_per_row": 4,
  "default_competition": null,
  "default_year": null
}
```

- `layout`: `"cards"`, `"table"` hoặc `"both"`.
- `cards_per_row`: 1–8 (dù đặt giá trị nào, lưới responsive vẫn tự co lại trên thiết bị di động).

## `admin`

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

!!! warning "Phạm vi xác thực của quản trị"
    Bề mặt quản trị phiên bản v0.1 (`/admin` + `/api/admin/*`) **không có sẵn cơ chế xác thực session tích hợp**. Các bản triển khai công khai có mở bề mặt này bắt buộc phải đặt nó sau một reverse proxy để kiểm soát truy cập (Basic Auth / OAuth / danh sách IP cho phép). Xem [`SECURITY.md`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/SECURITY.md). Đặt `enabled: false` để tắt hoàn toàn bề mặt ghi.

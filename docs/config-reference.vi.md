# Tài liệu tham khảo cấu hình

`honor.config.json` là toàn bộ cổng thông tin. Mọi khóa được xác thực bởi các mô hình Pydantic (`extra="forbid"`), vì vậy lỗi đánh máy sẽ thất bại to lớn khi tải. Tệp [`honor.schema.json`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/honor.schema.json) được cam kết cung cấp hoàn thiện tự động cho trình soạn thảo. Trỏ tệp của bạn vào nó:

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
| `editions` | array | ✓ (≥1) | Các cặp cuộc thi + năm bạn đã chạy. |
| `medals` | object | ✓ (≥1) | Sổ đăng ký huy chương toàn cầu: mã → định nghĩa. |
| `data_mapping` | object | | Ánh xạ tên cột để nhập. |
| `display` | object | | Bố cục UI + mặc định. |
| `admin` | object | | Chuyển đổi bề mặt quản trị viên + chế độ xác thực. |

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

- `slug` phải là kebab-case chữ thường; nó đặt tên cho tệp SQLite (`data/<slug>.db`).
- `locale` là `"en"` hoặc `"vi"`; chọn chuỗi UI.
- `branding.logo_url` phải bắt đầu bằng `/`, `http://`, `https://` hoặc `data:image/` (XSS sink đóng).

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

- `id` là một mã định danh an toàn URL `[A-Za-z0-9_-]+`.
- `medals` được viết hoa + khử trùng khi tải; mỗi mục **phải** tồn tại trong sổ đăng ký huy chương `medals` cấp cao nhất (xác thực giữa các trường).

## `editions[]`

```json
{ "competition_id": "demo-a", "year": 2025, "label": "Demo Olympiad A 2025" }
```

- `competition_id` phải tham chiếu một cuộc thi được khai báo (xác thực giữa các trường).
- Các cặp `(competition_id, year)` phải là duy nhất. Mỗi phiên bản được gán cho mỗi cuộc thi và mỗi năm.

## `medals`

```json
"medals": {
  "GOLD":   { "rank": 1, "label_en": "Gold Medal",   "label_vi": "Huy chương Vàng", "color": "#FFD700", "icon": "🥇" },
  "SILVER": { "rank": 2, "label_en": "Silver Medal", "label_vi": "Huy chương Bạc",  "color": "#C0C0C0", "icon": "🥈" }
}
```

- `rank` xác định thứ tự sắp xếp (thấp hơn = uy tín cao hơn; xếp hạng phải là duy nhất).
- `color` là chuỗi hex được sử dụng cho nền huy chương.

## `data_mapping`

Ánh xạ tiêu đề tệp nguồn của bạn vào các trường logic. Mặc định giả định các cột `candidate_no`, `name`, `grade`, `photo`, `school`, `rank`, `medal`, `subject`. `photo` là URL (https, đường dẫn tương đối tại site `/path` hoặc URI `data:`) được hiển thị dưới dạng avatar của học sinh:

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

Đặt bất kỳ cột tùy chọn nào thành `null` (hoặc bỏ qua nó) khi nguồn của bạn không có nó.

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
- `cards_per_row`: 1–8 (lưới đáp ứng bị sập trên thiết bị di động bất kể).

## `admin`

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

!!! warning "Phạm vi xác thực quản trị viên"
    Bề mặt quản trị viên v0.1 (`/admin` + `/api/admin/*`) **không có xác thực phiên làm việc tích hợp**. Các triển khai công khai phơi bày nó phải gating nó đằng sau proxy ngược (Xác thực cơ bản / OAuth / danh sách IP). Xem [`SECURITY.md`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/SECURITY.md). Đặt `enabled: false` để tắt toàn bộ bề mặt ghi.

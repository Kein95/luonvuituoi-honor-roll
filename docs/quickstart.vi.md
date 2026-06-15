# Bắt đầu nhanh

## 1. Cài đặt

Từ bản clone repo:

```bash
git clone https://github.com/Kein95/luonvuituoi-honor-roll
cd luonvuituoi-honor-roll
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ./packages/core -e ./packages/cli
```

## 2. Tạo dự án

```bash
lvt-honor init my-awards --name "My Awards" --slug my-awards --locale vi
cd my-awards
```

Lệnh này tạo `honor.config.json`, `api/index.py`, `requirements.txt`, và `README.md`.

## 3. Chuẩn bị kết quả

File nguồn có thể là CSV, Excel, hoặc JSON. Các cột được ánh xạ qua `data_mapping` trong cấu hình, nên đổi tên cột chỉ cần sửa cấu hình. Tối thiểu: cột `name` và `medal`.

=== "CSV"

    ```csv
    name,school,subject,medal,rank,candidate_no
    X,School,MATHS,Gold,2,S001
    Y,School,ENGLISH,Silver,8,S002
    ```

=== "JSON"

    ```json
    [
      {"name": "X", "school": "School", "subject": "MATH", "medal": "GOLD", "rank": "2"},
      {"name": "Y", "school": "School", "subject": "ENGLISH", "medal": "SILVER", "rank": "8"}
    ]
    ```

!!! tip "Chuẩn hoá môn + giải"
    Môn học được viết hoa (`Maths` → `MATHS`); giải được viết hoa và phải có trong bảng huy chương chung (`gold` → `GOLD`). Dòng thiếu tên hoặc giải không hợp lệ sẽ bị bỏ qua (kèm cảnh báo).

## 4. Nhập dữ liệu

```bash
lvt-honor import results.csv --competition demo-a --year 2025 --replace
```

`--replace` xoá các dòng cũ của kỳ đó trước, nên nhập lại là idempotent.

## 5. Chạy

```bash
lvt-honor dev          # → http://127.0.0.1:5000
```

Mở bảng vinh danh, trang `/search`, và `/admin` trong trình duyệt.

## 6. (Tuỳ chọn) Tạo dữ liệu giả

Để xem giao diện có dữ liệu trước khi có kết quả thật:

```bash
lvt-honor seed --count 60
```

## Bước tiếp theo

- [:material-cog: Tham khảo cấu hình](config-reference.md)
- [:material-sitemap: Kiến trúc](architecture.md)
- [:material-cloud: Triển khai](deploy-vercel.md)

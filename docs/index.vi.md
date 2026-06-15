# LUONVUITUOI-HONOR ROLL

> Bộ công cụ bảng vinh danh học sinh theo cấu hình. Chỉ cần file kết quả CSV/Excel/JSON + một file cấu hình → triển khai bảng vinh danh công khai (thẻ + bảng + thống kê), tra cứu học sinh, và trang quản trị lên Vercel hoặc Docker trong một buổi chiều.

Dự án anh em của [**LUONVUITUOI-CERT**](https://github.com/Kein95/luonvuituoi-cert) — bộ công cụ cổng chứng chỉ. Trong khi CERT *cấp phát và xác thực* chứng chỉ PDF, HONOR ROLL **xuất bản và vinh danh** các thành tích.

## Tại sao

Bạn tổ chức một cuộc thi (Demo Olympiad A, Demo Olympiad B, Olympic trường…) và có một bảng tính danh sách học sinh đạt giải. Bạn cần:

- Một **bảng vinh danh công khai** để học sinh, phụ huynh và trường xem thành tích.
- Một **trang tra cứu** để ai cũng có thể tìm tên và xem toàn bộ huy chương học sinh đó đạt được qua các kỳ.
- Một **trang quản trị** để thêm/sửa/xoá mà không cần đụng tới file.

Bộ công cụ này có đầy đủ ba thứ — theo cấu hình, không cần viết code.

## Tính năng

- :material-trophy: **Đa cuộc thi / đa năm** — một file cấu hình khai báo mọi cuộc thi, môn học và kỳ thi bạn đã tổ chức.
- :material-medal: **Bảng huy chương chung** — định nghĩa mỗi huy chương một lần (thứ hạng, nhãn Anh/Việt, màu, icon); badge hiển thị đồng nhất mọi nơi.
- :material-magnify: **Ba giao diện** — bảng vinh danh, tra cứu học sinh, quản trị.
- :material-file-import: **Nhập linh hoạt** — CSV / Excel / JSON, ánh xạ qua `data_mapping`.
- :material-cellphone-link: **Giao diện động, responsive** — desktop, tablet, mobile.
- :material-translate: **Đa ngôn ngữ** — Tiếng Anh + Tiếng Việt.
- :material-rocket-launch: **Sẵn sàng triển khai** — Vercel hoặc Docker.

## Demo tham chiếu

`examples/demo-honor/` đi kèm dữ liệu thật **Demo Olympiad A 2025** (66 giải thuộc MATHS / ENGLISH / SCIENCE).

```bash
cd examples/demo-honor
python prepare_demo.py
lvt-honor import data/demo-2025.json --competition demo-a --year 2025 --replace
lvt-honor dev
```

## Liên kết nhanh

- [:material-fast-forward: Bắt đầu nhanh](quickstart.vi.md)
- [:material-cog: Tham khảo cấu hình](config-reference.md)
- [:material-sitemap: Kiến trúc](architecture.md)
- [:material-cloud: Triển khai Vercel](deploy-vercel.md) · [:material-docker: Triển khai Docker](deploy-docker.md)

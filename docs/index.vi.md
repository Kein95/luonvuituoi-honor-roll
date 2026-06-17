---
hide:
  - navigation
  - toc
---

<div class="lvt-hero" markdown>

<img src="../assets/logo.svg" alt="Logo LUONVUITUOI-HONOR ROLL" class="lvt-hero-logo">

# LUONVUITUOI-HONOR ROLL

<p class="lvt-hero-tagline">
Bộ công cụ bảng vinh danh học sinh theo cấu hình. Chỉ cần file kết quả CSV/Excel/JSON và một file cấu hình — có ngay bảng vinh danh công khai kèm tra cứu, trang quản trị, và phòng trưng bày đa kỳ thi trong vài phút.
</p>

<div class="lvt-cta-row">
  <a href="https://honor-roll-vercel-demo.vercel.app" class="lvt-btn lvt-btn-primary">🌟 Xem demo</a>
  <a href="quickstart/" class="lvt-btn lvt-btn-primary">🚀 Bắt đầu nhanh (10 phút)</a>
  <a href="https://honor-roll-vercel-demo.vercel.app/login" class="lvt-btn lvt-btn-ghost" target="_blank" rel="noopener">🔐 Trang quản trị</a>
  <a href="https://github.com/Kein95/luonvuituoi-honor-roll" class="lvt-btn lvt-btn-ghost" target="_blank" rel="noopener">⭐ Xem trên GitHub</a>
</div>

<div class="lvt-badges">
  <img src="https://img.shields.io/github/v/release/Kein95/luonvuituoi-honor-roll?style=flat-square&color=7c5cff&label=release" alt="release">
  <img src="https://img.shields.io/github/license/Kein95/luonvuituoi-honor-roll?style=flat-square&color=7c5cff" alt="license">
  <img src="https://img.shields.io/github/actions/workflow/status/Kein95/luonvuituoi-honor-roll/test.yml?style=flat-square&color=7c5cff&label=tests" alt="tests">
  <img src="https://img.shields.io/github/stars/Kein95/luonvuituoi-honor-roll?style=flat-square&color=fb7185" alt="stars">
</div>

</div>

## Vì sao có dự án này

Tổ chức một cuộc thi, trao huy chương, chạy một kỳ olympic? Bạn thường cần một nơi trưng bày công khai để học sinh thấy thành tích, phụ huynh xác nhận kết quả, và nhà trường theo dõi huy chương — tất cả đều tra cứu được, trình bày đẹp, dễ quản lý. **LUONVUITUOI-HONOR ROLL cho bạn cả ba**, triển khai được lên gói miễn phí của Vercel hoặc bất kỳ máy chủ Docker nào, không cần viết khung sườn.

<div class="lvt-features" markdown>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🏆</span>
### Phòng trưng bày đa kỳ thi
Khai báo một hay nhiều cuộc thi qua các năm. Mỗi cuộc thi chạy độc lập; học sinh thấy mọi huy chương qua từng kỳ.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🎖️</span>
### Sổ huy chương linh hoạt
Khai báo mỗi huy chương một lần (hạng, nhãn, màu, icon). Huy hiệu luôn nhất quán. Nạp dữ liệu CSV/Excel/JSON.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🔍</span>
### Bảng vinh danh + tra cứu
Giao diện thẻ và bảng đẹp mắt. Khách tra cứu theo tên hoặc số báo danh, thấy ngay mọi thành tích.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🛠️</span>
### Trang quản trị tích hợp
Thêm, sửa, xoá mục mà không cần đụng tới file. Bảo vệ bằng mật khẩu, có nhật ký kiểm toán.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">⚡</span>
### Triển khai ở đâu cũng được
Một lệnh deploy Vercel (gói miễn phí), Dockerfile sản xuất, docker-compose — tuỳ hạ tầng của bạn.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🌐</span>
### Song ngữ & hợp mọi màn hình
Tiếng Việt + tiếng Anh. Giao diện responsive, có hiệu ứng, đẹp trên máy tính, máy tính bảng, điện thoại.
</div>

</div>

<div class="lvt-stats" markdown>

<div class="lvt-stat">
<div class="lvt-stat-num">10 phút</div>
<div class="lvt-stat-label">Lần deploy đầu</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">0</div>
<div class="lvt-stat-label">Dòng khung sườn</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">0đ</div>
<div class="lvt-stat-label">Gói Vercel miễn phí</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">MIT</div>
<div class="lvt-stat-label">Giấy phép</div>
</div>

</div>

## Bắt đầu

<div class="lvt-features" markdown>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🚀</span>
### [Bắt đầu nhanh →](quickstart.md)
Triển khai bảng vinh danh đầu tiên trong 10 phút. Scaffold bằng CLI, đi qua cấu hình, chạy local, đẩy lên Vercel.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">⚙️</span>
### [Cấu hình →](config-reference.md)
Mọi trường trong `honor.config.json` + biến môi trường đều được ghi rõ. Cách khai báo cuộc thi, huy chương và quy tắc.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🏛️</span>
### [Kiến trúc →](architecture.md)
Các mảnh ghép — handler, mô hình dữ liệu, chỉ mục tra cứu, xác thực quản trị, và lớp giao diện.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🔐</span>
### [Bảo mật →](security.md)
Checklist gia cố cho production. Xác thực quản trị, kiểm tra dữ liệu, giới hạn tần suất.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🛠️</span>
### [Vận hành →](operations.md)
Health probe, đọc log, chiến lược sao lưu, checklist xử lý sự cố.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">❓</span>
### [Khắc phục sự cố →](troubleshooting.md)
Các lỗi thường gặp, vấn đề nạp dữ liệu, và cách xử lý.
</div>

</div>

## Dự án anh em

- **[LUONVUITUOI-CERT](https://github.com/Kein95/luonvuituoi-cert)** — bộ công cụ cổng chứng chỉ. Cấp phát và xác thực chứng chỉ PDF kèm mã QR và trang quản trị. HONOR ROLL vinh danh thành tích, còn CERT chứng minh chúng.

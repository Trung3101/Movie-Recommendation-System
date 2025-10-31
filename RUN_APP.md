# 🎬 CineMate - Movie Recommendation System

## Hướng Dẫn Cài Đặt và Chạy Ứng Dụng

### 📋 Yêu Cầu Hệ Thống

- Python 3.8+
- RAM: 2GB minimum, 4GB khuyến nghị
- Storage: 1GB cho models
- Internet: Để tải poster từ TMDB

### 🚀 Bước 1: Cài Đặt Dependencies

Mở terminal và chạy:

```
pip install -r requirements.txt
và python là phiên bản dưới 3.11
```

### 📂 Bước 2: Kiểm Tra Cấu Trúc Thư Mục

Đảm bảo cấu trúc thư mục như sau:

```
Project/
│
├── GUI/
│   └── app.py
│
├── model_topN/
│   ├── Recommended.py
│   ├── recommendation_model.pkl
│   ├── svd_recommendation_system.pkl
│   ├── login_data.csv
│   └── movies_data.csv
│
├── templates/
│   ├── layout.html
│   ├── login.html
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── requirements.txt
└── RUN_APP.md (file này)
```

### ▶️ Bước 3: Chạy Ứng Dụng

```cmd
cd GUI
python app.py
```

Hoặc từ thư mục gốc:

```cmd
python GUI\app.py
```

### 🌐 Bước 4: Truy Cập Ứng Dụng

Mở trình duyệt và truy cập:

```
http://127.0.0.1:5000
```

hoặc

```
http://localhost:5000
```

### 🔐 Bước 5: Đăng Nhập/Đăng Ký

#### Đăng Ký Tài Khoản Mới:

1. Click tab "Đăng ký"
2. Nhập username (2-8 ký tự)
3. Nhập password (4 chữ số)
4. Xác nhận password
5. Click "Đăng ký"

#### Đăng Nhập:

1. Nhập username và password
2. Click "Đăng nhập"

### 🎯 Bước 6: Sử Dụng Hệ Thống

#### Tìm Kiếm Phim:

1. Nhập tên phim vào ô search (VD: "Inception", "The Matrix")
2. Click "Tìm Kiếm"
3. Hệ thống sẽ hiển thị 3 danh sách:
   - **Có Thể Bạn Muốn Xem**: Phim có tên tương đồng
   - **Phim Tương Tự**: Dựa trên nội dung
   - **Dành Riêng Cho Bạn**: Gợi ý cá nhân hóa

#### Đánh Giá Phim:

1. Click vào bất kỳ movie card nào
2. Modal chi tiết phim sẽ hiển thị
3. Chọn số sao (1-5)
4. Click "Đã Xem - Lưu Đánh Giá"
5. Danh sách "Dành Riêng Cho Bạn" sẽ tự động cập nhật

### 🛑 Dừng Ứng Dụng

Nhấn `CTRL + C` trong terminal để dừng server.

---

## 🔧 Xử Lý Lỗi Thường Gặp

### Lỗi: "FileNotFoundError"

**Nguyên nhân**: Thiếu file models hoặc data

**Giải pháp**:

```cmd
# Kiểm tra các file sau có tồn tại:
dir model_topN\*.pkl
dir model_topN\*.csv
```

### Lỗi: "Module not found"

**Nguyên nhân**: Chưa cài đặt dependencies

**Giải pháp**:

```cmd
pip install -r requirements.txt
```

### Lỗi: "Port 5000 already in use"

**Nguyên nhân**: Port đã được sử dụng bởi ứng dụng khác

**Giải pháp**: Sửa port trong `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Đổi thành 5001
```

### Lỗi: "ImportError: thefuzz"

**Nguyên nhân**: Chưa cài đặt thefuzz

**Giải pháp**:

```cmd
pip install thefuzz python-Levenshtein
```

---

## 📊 Thông Tin Model

### Content-Based Filtering

- **File**: `recommendation_model.pkl`
- **Size**: ~763 MB
- **Features**: genres, overview, movie_name, countries, director, cast
- **Technique**: TF-IDF + GloVe Word Embeddings

### Collaborative Filtering (SVD)

- **File**: `svd_recommendation_system.pkl`
- **Size**: ~100 MB
- **Algorithm**: Singular Value Decomposition
- **Metrics**:
  - RMSE: ~0.87
  - MAE: ~0.67
  - Hit Rate @ 10: ~38%

---

## 🎓 Công Nghệ Sử Dụng

### Backend:

- **Flask**: Web framework
- **Pandas**: Data processing
- **Scikit-learn**: TF-IDF, machine learning
- **Surprise**: SVD collaborative filtering
- **thefuzz**: Fuzzy string matching

### Frontend:

- **Bootstrap 5**: UI framework
- **jQuery**: AJAX interactions
- **Bootstrap Icons**: Icons

### Machine Learning:

- **Content-Based**: Cosine similarity với TF-IDF + Word2Vec
- **Collaborative Filtering**: SVD với RandomizedSearchCV

---

## 📝 Notes

⚠️ **Bảo mật**: Trong phiên bản demo này, password được lưu dạng plain text. Trong production nên sử dụng bcrypt hoặc argon2 để hash password.

💡 **Performance**: Models được load một lần duy nhất khi app khởi động để tối ưu hiệu suất.

🔄 **Session**: Sử dụng Flask session để quản lý đăng nhập.

---

## 👥 Thông Tin Dự Án

- **Tên**: CineMate - Movie Recommendation System
- **Môn học**: Data Mining
- **Trường**: HUIT
- **Năm**: 2025

---

## 📧 Liên Hệ

Nếu gặp vấn đề khi chạy ứng dụng, vui lòng liên hệ.

---

**Chúc bạn sử dụng CineMate vui vẻ! 🎬🍿**

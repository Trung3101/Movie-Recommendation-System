# Movie Recommendation System - CineMate 🎬

Hệ thống gợi ý phim thông minh sử dụng Machine Learning với 2 phương pháp chính và ứng dụng web Flask hoàn chỉnh.

## 🌟 Tính Năng Chính

- ✅ **Tìm Kiếm Phim Thông Minh**: Fuzzy matching với thefuzz
- ✅ **Content-Based Filtering**: Gợi ý dựa trên nội dung phim
- ✅ **Collaborative Filtering**: Gợi ý cá nhân hóa với SVD
- ✅ **Web Application**: Giao diện đẹp với Flask + Bootstrap 5
- ✅ **Đăng Ký/Đăng Nhập**: Quản lý user và session
- ✅ **Đánh Giá Phim**: Rating system và cập nhật gợi ý real-time

## 🚀 Quick Start - Chạy Web App

```cmd
cd "c:\Users\Cao Anh\HUIT - Học Tập\Năm 3\Học ở Trường\Data Mining\Project"
pip install -r requirements.txt
cd GUI
python app.py
```

Truy cập: http://localhost:5000

📖 **Chi tiết**: Xem file [RUN_APP.md](RUN_APP.md)

## 🎬 Models

### 1. Content-Based Filtering (`recommendation_model.pkl`)

- **Mục đích**: Đề xuất phim tương tự dựa trên nội dung
- **Input**: Danh sách tên phim
- **Output**: Top N phim có nội dung tương tự
- **Kích thước**: ~763 MB

### 2. Collaborative Filtering (`svd_recommendation_system.pkl`)

- **Mục đích**: Đề xuất phim dựa trên lịch sử xem của người dùng
- **Input**: User ID
- **Output**: Top N phim được dự đoán có rating cao
- **Kích thước**: ~100 MB

## 📚 Quick Start

### Installation

```bash
pip install pandas numpy scikit-learn scikit-surprise scipy
```

### Content-Based Example

```python
import pickle
import pandas as pd
import numpy as np

# Load model
with open('model_topN/recommendation_model.pkl', 'rb') as f:
    model = pickle.load(f)

data = model['data']
cosine_sim_combined = model['cosine_sim_combined']

# Get recommendations
def get_recommendations(movie_list, top_n=10):
    indices_list = []
    for movie in movie_list:
        idx = data[data['movie_name'].str.lower() == movie.lower()].index
        if len(idx) > 0:
            indices_list.append(idx[0])

    if not indices_list:
        return pd.DataFrame()

    sim_scores_list = [cosine_sim_combined[idx] for idx in indices_list]
    avg_sim_scores = np.mean(sim_scores_list, axis=0)

    sim_scores = [(i, score) for i, score in enumerate(avg_sim_scores)
                  if i not in indices_list]
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i for i, _ in sim_scores[:top_n]]
    result = data.iloc[top_indices].copy()

    return result

# Usage
recommendations = get_recommendations(["Inception", "The Matrix"], top_n=10)
print(recommendations[['movie_name', 'genres']])
```

### Collaborative Filtering Example

```python
from model_topN.svd_recommender import SVDRecommender

# Load model
recommender = SVDRecommender('model_topN/svd_recommendation_system.pkl')

# Get recommendations for user
user_id = 123
recommendations = recommender.recommend_movies(user_id, n=10)

print(f"Top 10 recommendations for User {user_id}:")
print(recommendations[['movie_name', 'predicted_rating']])

# Get user's watch history
watched = recommender.get_user_watched_movies(user_id)
print(f"\nUser has watched {len(watched)} movies")
```

## 📖 Full Documentation

Xem file [`docs/MODEL_USAGE_GUIDE.md`](docs/MODEL_USAGE_GUIDE.md) để có hướng dẫn chi tiết về:

- Cách sử dụng từng model
- Helper classes và utilities
- API examples (Flask, FastAPI)
- GUI integration
- Hybrid approaches
- Troubleshooting
- Performance optimization

## 🗂️ Project Structure

```
Project/
├── GUI/
│   └── app.py                           # Flask web application
├── model_topN/
│   ├── Recommended.py                   # Recommendation functions
│   ├── recommendation_model.pkl         # Content-Based model
│   ├── svd_recommendation_system.pkl    # Collaborative model
│   ├── login_data.csv                   # User credentials
│   └── movies_data.csv                  # Movie data backup
├── templates/
│   ├── layout.html                      # Base template
│   ├── login.html                       # Login/Register page
│   └── index.html                       # Main page
├── static/
│   ├── css/
│   │   └── style.css                    # Custom styles
│   └── js/
│       └── script.js                    # AJAX interactions
├── notebooks/
│   └── Make_Features.ipynb              # Training notebook
├── data/
│   ├── final_data.csv
│   └── ratings_final.csv
├── docs/
│   └── MODEL_USAGE_GUIDE.md             # Full documentation
├── requirements.txt                     # Python dependencies
├── RUN_APP.md                          # Deployment guide
└── README.md                           # This file
```

## 📊 Model Performance

### Content-Based Filtering

- **Features**: genres, overview, movie_name, countries, director, cast
- **Technique**: TF-IDF + GloVe Word Embeddings
- **Movies**: 10,000
- **Accuracy**: High for similar genres/directors

### Collaborative Filtering (SVD)

- **Algorithm**: Singular Value Decomposition
- **Users**: ~45,000
- **Movies**: 10,000
- **Ratings**: ~50,000
- **RMSE**: ~0.87
- **MAE**: ~0.67
- **Hit Rate @ 10**: ~38%

## 🚀 Use Cases

### Content-Based Best For:

- ✅ New users (cold start problem)
- ✅ Finding similar movies
- ✅ Genre/director-based recommendations
- ✅ No user history needed

### Collaborative Best For:

- ✅ Users with watch history
- ✅ Personalized recommendations
- ✅ Discovering new genres
- ✅ Better accuracy with more data

## 💡 Hybrid Approach

Kết hợp cả 2 models để có kết quả tốt nhất:

```python
def hybrid_recommendations(user_id, movie_list, weight_cf=0.6, weight_cb=0.4, n=10):
    # Get CF recommendations
    cf_recs = recommender.recommend_movies(user_id, n=20)
    cf_scores = {row['movieId']: row['predicted_rating']
                 for _, row in cf_recs.iterrows()}

    # Get CB recommendations
    cb_recs = get_recommendations(movie_list, top_n=20)
    cb_scores = {row['id']: row['similarity_score']
                 for _, row in cb_recs.iterrows()}

    # Combine and normalize
    combined_scores = {}
    for movie_id in set(cf_scores.keys()) | set(cb_scores.keys()):
        cf = cf_scores.get(movie_id, 0) / 5.0  # Normalize to 0-1
        cb = cb_scores.get(movie_id, 0)
        combined_scores[movie_id] = weight_cf * cf + weight_cb * cb

    # Get top N
    top_ids = sorted(combined_scores.keys(),
                    key=lambda x: combined_scores[x],
                    reverse=True)[:n]

    return data[data['id'].isin(top_ids)]
```

## 🛠️ System Requirements

- **Python**: 3.7+
- **RAM**: 2 GB minimum, 4 GB recommended
- **Storage**: 1 GB for models
- **CPU**: 2+ cores

## 📝 License


## 👥 Contributors

- [Trương Phú Triệu]
- [Đoàn Trần Cao Anh]
- [Trần Cẩm Tú]

## 📧 Contact

- Email: [truongphutrieu18@gmail.com]

---

**Last Updated**: October 15, 2025

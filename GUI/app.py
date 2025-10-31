"""
CineMate - Movie Recommendation Web Application
Flask Backend Application
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import os
import sys
import pandas as pd
import numpy as np
import pickle
import random

# ⚠️ QUAN TRỌNG: Thêm đường dẫn TRƯỚC KHI import model_topN
# app.py nằm trong GUI/, cần truy cập ../model_topN/
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Bây giờ mới import các hàm từ model_topN
from model_topN.Recommended import (
    get_related_movies,
    get_recommendations_combined,
    get_top_n_recommendations,
    format_results_for_json
)

# Khởi tạo Flask app
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Cấu hình SECRET_KEY cho session (trong production nên dùng biến môi trường)
app.config['SECRET_KEY'] = 'cinemate_secret_key_2025_dmproject_huit'

# ============================================================================
# GLOBAL VARIABLES - Load models và data MỘT LẦN DUY NHẤT khi app khởi động
# ============================================================================
print("=" * 80)
print("🎬 CINEMATE - KHỞI ĐỘNG ỨNG DỤNG")
print("=" * 80)

# Đường dẫn đến thư mục chứa models và data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'model_topN')

try:
    print("\n📂 Đang tải models và dữ liệu...")

    # 1. Load Content-Based Recommendation Model
    cb_model_path = os.path.join(MODEL_DIR, 'recommendation_model.pkl')
    print(f"   • Loading {cb_model_path}...")
    with open(cb_model_path, 'rb') as f:
        CONTENT_BASED_MODEL = pickle.load(f)
    print("   ✓ Content-Based Model loaded successfully")

    # 2. Load SVD Recommendation Model
    svd_model_path = os.path.join(MODEL_DIR, 'svd_recommendation_system.pkl')
    print(f"   • Loading {svd_model_path}...")
    with open(svd_model_path, 'rb') as f:
        SVD_MODEL = pickle.load(f)
    print("   ✓ SVD Model loaded successfully")

    # 3. Load Movies Data
    movies_path = os.path.join(MODEL_DIR, 'movies_data.csv')
    print(f"   • Loading {movies_path}...")
    MOVIES_DF = pd.read_csv(movies_path)
    print(f"   ✓ Movies Data loaded: {len(MOVIES_DF):,} movies")

    # 4. Load Login Data
    login_path = os.path.join(MODEL_DIR, 'login_data.csv')
    print(f"   • Loading {login_path}...")
    LOGIN_DF = pd.read_csv(login_path)
    print(f"   ✓ Login Data loaded: {len(LOGIN_DF):,} users")

    print("\n✅ TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC TẢI THÀNH CÔNG!")
    print("=" * 80)

except FileNotFoundError as e:
    print(f"\n❌ LỖI NGHIÊM TRỌNG: Không tìm thấy file cần thiết!")
    print(f"   Chi tiết: {e}")
    print("\n⚠️  Ứng dụng không thể khởi động. Vui lòng kiểm tra các file sau:")
    print(f"   • {cb_model_path}")
    print(f"   • {svd_model_path}")
    print(f"   • {movies_path}")
    print(f"   • {login_path}")
    print("=" * 80)
    sys.exit(1)

except Exception as e:
    print(f"\n❌ LỖI NGHIÊM TRỌNG: {e}")
    print("=" * 80)
    sys.exit(1)


# ============================================================================
# ROUTING - Các endpoint của ứng dụng
# ============================================================================

@app.route('/')
def index():
    """
    Trang chủ - Yêu cầu đăng nhập
    """
    # Kiểm tra xem user đã đăng nhập chưa
    if 'userId' not in session:
        return redirect(url_for('login'))

    # Render trang chủ
    return render_template('index.html', username=session.get('username'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Trang đăng nhập
    GET: Hiển thị form đăng nhập
    POST: Xử lý đăng nhập
    """
    if request.method == 'GET':
        # Hiển thị trang login
        return render_template('login.html', error=None, success=None)

    # POST: Xử lý đăng nhập
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    print(f"\n🔐 DEBUG Login attempt:")
    print(f"   - Input username: '{username}' (length: {len(username)})")
    print(f"   - Input password: '{password}' (length: {len(password)})")

    # Validate input
    if not username or not password:
        return render_template('login.html',
                               error='Vui lòng nhập đầy đủ username và password',
                               success=None)

    # Reload LOGIN_DF from file để đảm bảo có dữ liệu mới nhất
    global LOGIN_DF
    try:
        login_path = os.path.join(MODEL_DIR, 'login_data.csv')
        LOGIN_DF = pd.read_csv(login_path)

        # Clean data: strip whitespace from username and password columns
        LOGIN_DF['username'] = LOGIN_DF['username'].astype(str).str.strip()
        LOGIN_DF['password'] = LOGIN_DF['password'].astype(str).str.strip()

        print(f"   ✓ Reloaded LOGIN_DF: {len(LOGIN_DF)} users")
        print(f"   Sample usernames: {LOGIN_DF['username'].head(5).tolist()}")
    except Exception as e:
        print(f"   ❌ Error reloading login data: {e}")

    # Kiểm tra thông tin đăng nhập
    user = LOGIN_DF[(LOGIN_DF['username'] == username) &
                    (LOGIN_DF['password'] == password)]

    print(f"   - Found {len(user)} matching user(s)")

    if user.empty:
        # Debug: kiểm tra từng điều kiện
        username_match = LOGIN_DF[LOGIN_DF['username'] == username]
        password_match = LOGIN_DF[LOGIN_DF['password'] == password]

        print(f"   - Username matches: {len(username_match)}")
        print(f"   - Password matches: {len(password_match)}")

        if len(username_match) > 0:
            stored_password = username_match.iloc[0]['password']
            print(
                f"   - Stored password for '{username}': '{stored_password}'")
            print(f"   - Password match: {stored_password == password}")

        return render_template('login.html',
                               error='Username hoặc password không đúng',
                               success=None)

    # Đăng nhập thành công
    session['userId'] = int(user.iloc[0]['userId'])
    session['username'] = username

    print(
        f"   ✅ Login successful for user: {username} (ID: {session['userId']})")

    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    """
    Xử lý đăng ký tài khoản mới
    """
    global LOGIN_DF

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()

    # Validate input
    if not username or not password or not password_confirm:
        return render_template('login.html',
                               error='Vui lòng nhập đầy đủ thông tin',
                               success=None)

    if password != password_confirm:
        return render_template('login.html',
                               error='Mật khẩu xác nhận không khớp',
                               success=None)

    if len(username) < 2 or len(username) > 8:
        return render_template('login.html',
                               error='Username phải từ 2-8 ký tự',
                               success=None)

    if len(password) != 4 or not password.isdigit():
        return render_template('login.html',
                               error='Password phải là 4 chữ số',
                               success=None)

    # Kiểm tra username đã tồn tại
    if username in LOGIN_DF['username'].values:
        return render_template('login.html',
                               error='Username đã tồn tại',
                               success=None)

    # Tạo userId mới (6 chữ số ngẫu nhiên)
    max_attempts = 100
    for _ in range(max_attempts):
        new_user_id = random.randint(100000, 999999)
        if new_user_id not in LOGIN_DF['userId'].values:
            break
    else:
        return render_template('login.html',
                               error='Không thể tạo userId mới, vui lòng thử lại',
                               success=None)

    # Thêm user mới vào LOGIN_DF
    new_user = pd.DataFrame({
        'userId': [new_user_id],
        'username': [username.strip()],  # Đảm bảo strip whitespace
        'password': [password.strip()]   # Đảm bảo strip whitespace
    })

    LOGIN_DF = pd.concat([LOGIN_DF, new_user], ignore_index=True)

    # Lưu lại file login_data.csv
    try:
        login_path = os.path.join(MODEL_DIR, 'login_data.csv')
        LOGIN_DF.to_csv(login_path, index=False)
        print(f"✓ New user registered: {username} (ID: {new_user_id})")
        print(f"   - Total users in database: {len(LOGIN_DF)}")
    except Exception as e:
        print(f"❌ Error saving login data: {e}")
        return render_template('login.html',
                               error='Lỗi khi lưu thông tin đăng ký',
                               success=None)

    # Chuyển hướng về login với thông báo thành công
    return render_template('login.html',
                           error=None,
                           success='Đăng ký thành công! Vui lòng đăng nhập.')


@app.route('/logout')
def logout():
    """
    Đăng xuất - Xóa session
    """
    session.clear()
    return redirect(url_for('login'))


@app.route('/search', methods=['POST'])
def search():
    """
    AJAX Endpoint: Tìm kiếm và gợi ý phim

    Returns:
        JSON: {
            'related': [...],
            'similar': [...],
            'personalized': [...]
        }
    """
    try:
        # Lấy movie_name từ request
        data = request.get_json()
        movie_name = data.get('movie_name', '').strip()

        if not movie_name:
            return jsonify({
                'error': 'Vui lòng nhập tên phim',
                'related': [],
                'similar': [],
                'personalized': []
            }), 400

        # Lấy userId từ session
        user_id = session.get('userId')
        if not user_id:
            return jsonify({'error': 'Chưa đăng nhập'}), 401

        # Xác định state (new_user hay old_user)
        ratings_data = SVD_MODEL.get('ratings_data')
        if ratings_data is not None:
            user_ratings = ratings_data[ratings_data['userId'] == user_id]
            state = 'old_user' if not user_ratings.empty else 'new_user'
        else:
            state = 'new_user'

        print(
            f"\n🔍 Search request: '{movie_name}' by User {user_id} ({state})")

        # 1. Tìm phim có tên tương đồng
        related_movies = get_related_movies(movie_name, MOVIES_DF)
        related_list = format_results_for_json(related_movies)

        # 2. Gợi ý phim tương tự (Content-Based)
        similar_movies = get_recommendations_combined(
            movie_name, MOVIES_DF, CONTENT_BASED_MODEL)
        similar_list = format_results_for_json(similar_movies)

        # 3. Gợi ý cá nhân hóa (Collaborative Filtering)
        personalized_movies = get_top_n_recommendations(
            user_id, state, MOVIES_DF, SVD_MODEL)
        personalized_list = format_results_for_json(personalized_movies)

        print(f"   • Related: {len(related_list)} movies")
        print(f"   • Similar: {len(similar_list)} movies")
        print(f"   • Personalized: {len(personalized_list)} movies")

        return jsonify({
            'related': related_list,
            'similar': similar_list,
            'personalized': personalized_list
        })

    except Exception as e:
        print(f"❌ Error in /search endpoint: {e}")
        return jsonify({
            'error': 'Lỗi khi tìm kiếm phim',
            'related': [],
            'similar': [],
            'personalized': []
        }), 500


@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    """
    AJAX Endpoint: Đánh giá phim và cập nhật gợi ý cá nhân hóa

    Returns:
        JSON: {
            'personalized': [...]
        }
    """
    try:
        # Lấy data từ request
        data = request.get_json()
        user_id = session.get('userId')
        movie_id = data.get('movieId')
        rating = data.get('rating')

        print(f"\n⭐ DEBUG rate_movie:")
        print(f"   - Received data: {data}")
        print(f"   - user_id: {user_id} (type: {type(user_id)})")
        print(f"   - movie_id: {movie_id} (type: {type(movie_id)})")
        print(f"   - rating: {rating} (type: {type(rating)})")

        if not user_id:
            return jsonify({'error': 'Chưa đăng nhập'}), 401

        if not movie_id or not rating:
            return jsonify({'error': 'Thiếu thông tin movieId hoặc rating'}), 400

        # Kiểm tra movie_id có tồn tại trong MOVIES_DF không
        movie_exists = movie_id in MOVIES_DF['id'].values
        print(f"   - Movie exists in MOVIES_DF: {movie_exists}")

        if not movie_exists:
            print(f"   ❌ Movie ID {movie_id} NOT FOUND in MOVIES_DF!")
            print(
                f"   - Sample IDs from MOVIES_DF: {MOVIES_DF['id'].head(10).tolist()}")
            return jsonify({
                'error': f'Không tìm thấy thông tin phim! (ID: {movie_id})',
                'personalized': []
            }), 404

        print(
            f"\n⭐ Rate movie: User {user_id} rated Movie {movie_id} with {rating} stars")

        # Lưu rating (trong thực tế nên lưu vào database hoặc file CSV)
        # Hiện tại chỉ cập nhật trong memory
        ratings_data = SVD_MODEL.get('ratings_data')
        if ratings_data is not None:
            new_rating = pd.DataFrame({
                'userId': [user_id],
                'movieId': [movie_id],
                'rating': [rating]
            })

            # Cập nhật hoặc thêm rating mới
            mask = (ratings_data['userId'] == user_id) & (
                ratings_data['movieId'] == movie_id)
            if mask.any():
                ratings_data.loc[mask, 'rating'] = rating
                print(f"   ✓ Updated existing rating")
            else:
                ratings_data = pd.concat(
                    [ratings_data, new_rating], ignore_index=True)
                print(f"   ✓ Added new rating")

            SVD_MODEL['ratings_data'] = ratings_data

        # Gọi lại hàm gợi ý cá nhân hóa với state='old_user'
        personalized_movies = get_top_n_recommendations(
            user_id, 'old_user', MOVIES_DF, SVD_MODEL)
        personalized_list = format_results_for_json(personalized_movies)

        print(f"   • Updated personalized: {len(personalized_list)} movies")

        return jsonify({
            'personalized': personalized_list,
            'message': 'Đã lưu đánh giá thành công'
        })

    except Exception as e:
        print(f"❌ Error in /rate_movie endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Lỗi khi lưu đánh giá: {str(e)}',
            'personalized': []
        }), 500


@app.route('/filter', methods=['POST'])
def filter_movies():
    """
    AJAX Endpoint: Lọc phim theo nhiều tiêu chí

    Request JSON:
        {
            'search_query': str (optional),
            'countries': [str] (optional),
            'genres': [str] (optional),
            'years': [int] (optional),
            'sort_by': str (optional: 'vote_count', 'revenue', 'budget', 'popularity')
        }

    Returns:
        JSON: {
            'movies': [...],  # Tối đa 30 phim
            'total': int
        }
    """
    try:
        # Lấy data từ request
        data = request.get_json()

        search_query = data.get('search_query', '').strip()
        countries = data.get('countries', [])
        genres = data.get('genres', [])
        years = data.get('years', [])
        sort_by = data.get('sort_by', 'popularity')  # Default sort

        print(f"\n🔍 DEBUG filter_movies:")
        print(f"   - search_query: '{search_query}'")
        print(f"   - countries: {countries}")
        print(f"   - genres: {genres}")
        print(f"   - years: {years}")
        print(f"   - sort_by: {sort_by}")

        # Bắt đầu với toàn bộ dataset
        filtered_df = MOVIES_DF.copy()

        # Filter 1: Search query (tìm trong movie_name)
        if search_query:
            filtered_df = filtered_df[
                filtered_df['movie_name'].str.contains(
                    search_query, case=False, na=False)
            ]
            print(f"   • After search filter: {len(filtered_df)} movies")

        # Filter 2: Countries
        if countries and len(countries) > 0:
            # production_countries có thể chứa nhiều quốc gia
            country_mask = filtered_df['production_countries'].apply(
                lambda x: any(country in str(x)
                              for country in countries) if pd.notna(x) else False
            )
            filtered_df = filtered_df[country_mask]
            print(f"   • After countries filter: {len(filtered_df)} movies")

        # Filter 3: Genres (split by |)
        if genres and len(genres) > 0:
            genre_mask = filtered_df['genres'].apply(
                lambda x: any(genre in str(x).split('|')
                              for genre in genres) if pd.notna(x) else False
            )
            filtered_df = filtered_df[genre_mask]
            print(f"   • After genres filter: {len(filtered_df)} movies")

        # Filter 4: Years
        if years and len(years) > 0:
            filtered_df = filtered_df[filtered_df['release_year'].isin(years)]
            print(f"   • After years filter: {len(filtered_df)} movies")

        # Sort
        if sort_by in ['vote_count', 'revenue', 'budget', 'popularity']:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
            print(f"   • Sorted by: {sort_by}")

        # Lấy tối đa 30 phim đầu tiên
        result_df = filtered_df.head(30)

        # Chuyển đổi sang JSON format
        movies_list = format_results_for_json(result_df)

        total_count = len(filtered_df)
        returned_count = len(movies_list)

        print(f"\n✅ Filter complete:")
        print(f"   • Total matching: {total_count}")
        print(f"   • Returned: {returned_count}")

        return jsonify({
            'movies': movies_list,
            'total': total_count,
            'returned': returned_count
        })

    except Exception as e:
        print(f"❌ Error in /filter endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Lỗi khi lọc phim: {str(e)}',
            'movies': [],
            'total': 0
        }), 500


@app.route('/filter_data', methods=['GET'])
def get_filter_data():
    """
    API Endpoint: Trả về filter data (genres, countries, years, sort options)

    Returns:
        JSON: filter_data from filter_data.json
    """
    try:
        import json
        filter_data_path = os.path.join(MODEL_DIR, 'filter_data.json')

        with open(filter_data_path, 'r', encoding='utf-8') as f:
            filter_data = json.load(f)

        print(f"✓ Loaded filter data: {len(filter_data.get('genres', []))} genres, "
              f"{len(filter_data.get('production_countries', []))} countries")

        return jsonify(filter_data)

    except Exception as e:
        print(f"❌ Error loading filter data: {e}")
        return jsonify({
            'error': 'Không thể tải dữ liệu bộ lọc',
            'genres': [],
            'production_countries': [],
            'release_years': [],
            'sort_options': []
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Xử lý lỗi 404"""
    return render_template('login.html',
                           error='Trang không tồn tại',
                           success=None), 404


@app.errorhandler(500)
def internal_error(error):
    """Xử lý lỗi 500"""
    print(f"❌ Internal Server Error: {error}")
    return render_template('login.html',
                           error='Lỗi máy chủ nội bộ',
                           success=None), 500


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 STARTING CINEMATE SERVER")
    print("=" * 80)
    print("\n📍 Access the application at: http://127.0.0.1:5000")
    print("🔒 Press CTRL+C to stop the server\n")

    # Chạy ứng dụng ở chế độ debug
    app.run(debug=True, host='0.0.0.0', port=5000)

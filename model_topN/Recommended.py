"""
Module chứa các hàm gợi ý phim cho ứng dụng CineMate
Bao gồm: Content-Based, Collaborative Filtering, và Search
"""

import pandas as pd
import numpy as np
import pickle
from thefuzz import process


def get_related_movies(movie_name, movies_df):
    """
    Tìm kiếm các phim có tên gần giống với movie_name

    Args:
        movie_name (str): Tên phim cần tìm
        movies_df (DataFrame): DataFrame chứa thông tin tất cả phim

    Returns:
        DataFrame: Top 10 phim có tên tương đồng với các cột:
                   [movie_name, genres, director, release_year, poster_path]
    """
    try:
        # Kiểm tra input
        if movies_df is None or movies_df.empty:
            print("⚠️  Warning: movies_df is empty or None")
            return pd.DataFrame()

        if 'movie_name' not in movies_df.columns:
            print("⚠️  Warning: 'movie_name' column not found in movies_df")
            return pd.DataFrame()

        if not movie_name or not isinstance(movie_name, str):
            print("⚠️  Warning: Invalid movie_name")
            return pd.DataFrame()

        # Làm sạch input
        movie_name = movie_name.strip()

        # Sử dụng thefuzz để tìm các phim tương đồng
        movie_list = movies_df['movie_name'].tolist()
        matches = process.extract(movie_name, movie_list, limit=10)

        # Lấy tên các phim match
        matched_names = [match[0] for match in matches]

        # Lọc và lấy thông tin từ movies_df
        results = movies_df[movies_df['movie_name'].isin(matched_names)].copy()

        # Đảm bảo có đủ các cột cần thiết (BẮT BUỘC PHẢI CÓ 'id' và 'overview')
        required_columns = ['id', 'movie_name', 'genres',
                            'director', 'release_year', 'poster_path', 'overview']
        for col in required_columns:
            if col not in results.columns:
                results[col] = None

        # Chọn và sắp xếp theo thứ tự match
        results = results[required_columns].head(10)

        return results

    except Exception as e:
        print(f"❌ Error in get_related_movies: {e}")
        return pd.DataFrame()


def get_recommendations_combined(movie_name, movies_df, model):
    """
    Gợi ý phim dựa trên nội dung (Content-Based Filtering)

    Args:
        movie_name (str): Tên phim làm cơ sở để gợi ý
        movies_df (DataFrame): DataFrame chứa thông tin tất cả phim
        model (dict): Dictionary chứa 'data' và 'cosine_sim_combined'

    Returns:
        DataFrame: Top 10 phim tương tự với các cột:
                   [movie_name, genres, director, release_year, poster_path]
    """
    try:
        # Kiểm tra input
        if not movie_name or not isinstance(movie_name, str):
            print("⚠️  Warning: Invalid movie_name")
            return pd.DataFrame()

        if movies_df is None or movies_df.empty:
            print("⚠️  Warning: movies_df is empty or None")
            return pd.DataFrame()

        if model is None:
            print("⚠️  Warning: Model is None")
            return pd.DataFrame()

        # DEBUG: In ra thông tin model
        print(f"📊 DEBUG Model info:")
        print(f"   - Model type: {type(model)}")
        print(
            f"   - Model keys: {list(model.keys()) if isinstance(model, dict) else 'Not a dict'}")

        if 'cosine_sim_combined' not in model:
            print("⚠️  Warning: 'cosine_sim_combined' not in model")
            print(f"   Available keys: {list(model.keys())}")
            return pd.DataFrame()

        # Làm sạch input
        movie_name = movie_name.strip()

        # Lấy data và cosine similarity matrix từ model
        data = model.get('data', movies_df)
        cosine_sim = model['cosine_sim_combined']

        print(f"📊 DEBUG Data info:")
        print(f"   - Data shape: {data.shape}")
        print(f"   - Cosine sim shape: {cosine_sim.shape}")

        # Tìm index của phim trong data
        movie_name_lower = movie_name.lower()
        indices = data[data['movie_name'].str.lower() ==
                       movie_name_lower].index

        if len(indices) == 0:
            # Thử tìm kiếm gần đúng với fuzzy matching
            print(
                f"⚠️  Warning: Movie '{movie_name}' not found exactly, trying fuzzy search...")
            from thefuzz import process
            movie_list = data['movie_name'].tolist()
            matches = process.extract(movie_name, movie_list, limit=1)
            if matches and matches[0][1] >= 70:  # Độ tương đồng >= 70%
                matched_name = matches[0][0]
                print(
                    f"   ✓ Found similar movie: '{matched_name}' (score: {matches[0][1]})")
                indices = data[data['movie_name'] == matched_name].index
            else:
                print(f"   ✗ No similar movie found")
                return pd.DataFrame()

        idx = indices[0]
        print(f"   - Using movie at index: {idx}")

        # Lấy vector similarity scores
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sắp xếp theo điểm tương đồng (bỏ qua phim đầu tiên vì là chính nó)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Lấy top 10

        # Lấy indices của các phim
        movie_indices = [i[0] for i in sim_scores]

        print(f"   - Found {len(movie_indices)} similar movies")

        # Lấy thông tin phim từ data
        results = data.iloc[movie_indices].copy()

        # Đảm bảo có đủ các cột cần thiết (BẮT BUỘC PHẢI CÓ 'id' và 'overview')
        required_columns = ['id', 'movie_name', 'genres',
                            'director', 'release_year', 'poster_path', 'overview']
        for col in required_columns:
            if col not in results.columns:
                results[col] = None

        results = results[required_columns]

        return results

    except KeyError as e:
        print(f"⚠️  Warning: KeyError in get_recommendations_combined: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error in get_recommendations_combined: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def get_top_n_recommendations(user_id, state, movies_df, svd_model):
    """
    Gợi ý phim cá nhân hóa (Collaborative Filtering)

    Args:
        user_id (int): ID của người dùng
        state (str): 'new_user' hoặc 'old_user'
        movies_df (DataFrame): DataFrame chứa thông tin tất cả phim
        svd_model (dict): Dictionary chứa SVD model và dữ liệu liên quan

    Returns:
        DataFrame: Top 10 phim được gợi ý với các cột:
                   [movie_name, genres, director, release_year, poster_path]
    """
    try:
        # Kiểm tra input
        if movies_df is None or movies_df.empty:
            print("⚠️  Warning: movies_df is empty or None")
            return pd.DataFrame()

        if not isinstance(state, str) or state not in ['new_user', 'old_user']:
            print("⚠️  Warning: Invalid state. Must be 'new_user' or 'old_user'")
            state = 'new_user'

        # NEW USER: Gợi ý các phim phổ biến
        if state == 'new_user':
            # Kiểm tra cột popularity
            if 'popularity' not in movies_df.columns:
                print(
                    "⚠️  Warning: 'popularity' column not found, using random selection")
                results = movies_df.sample(n=min(10, len(movies_df))).copy()
            else:
                # Sắp xếp theo popularity và lấy top 10
                results = movies_df.nlargest(10, 'popularity').copy()

            # Đảm bảo có đủ các cột cần thiết (BẮT BUỘC PHẢI CÓ 'id' và 'overview')
            required_columns = ['id', 'movie_name', 'genres',
                                'director', 'release_year', 'poster_path', 'overview']
            for col in required_columns:
                if col not in results.columns:
                    results[col] = None

            return results[required_columns]

        # OLD USER: Gợi ý dựa trên SVD model
        else:
            if svd_model is None:
                print("⚠️  Warning: svd_model is None, falling back to popular movies")
                return get_top_n_recommendations(user_id, 'new_user', movies_df, None)

            # Lấy các thành phần từ svd_model
            model = svd_model.get('model')
            ratings_data = svd_model.get('ratings_data')

            if model is None or ratings_data is None:
                print("⚠️  Warning: Invalid svd_model structure")
                return get_top_n_recommendations(user_id, 'new_user', movies_df, None)

            # Kiểm tra user_id có tồn tại không
            user_ratings = ratings_data[ratings_data['userId'] == user_id]

            if user_ratings.empty:
                print(
                    f"⚠️  Warning: User {user_id} not found in ratings, falling back to popular movies")
                return get_top_n_recommendations(user_id, 'new_user', movies_df, None)

            # Lấy danh sách phim đã xem
            watched_movies = set(user_ratings['movieId'].values)

            # Lấy danh sách tất cả phim
            all_movies = set(
                movies_df['id'].values) if 'id' in movies_df.columns else set()

            # Lọc phim chưa xem
            unwatched_movies = all_movies - watched_movies

            if not unwatched_movies:
                print(f"⚠️  Warning: User {user_id} has watched all movies")
                return get_top_n_recommendations(user_id, 'new_user', movies_df, None)

            # Dự đoán rating cho các phim chưa xem
            predictions = []
            for movie_id in unwatched_movies:
                try:
                    pred = model.predict(user_id, movie_id)
                    predictions.append((movie_id, pred.est))
                except:
                    continue

            if not predictions:
                print(
                    f"⚠️  Warning: Could not generate predictions for user {user_id}")
                return get_top_n_recommendations(user_id, 'new_user', movies_df, None)

            # Sắp xếp và lấy top 10
            predictions.sort(key=lambda x: x[1], reverse=True)
            top_movie_ids = [pred[0] for pred in predictions[:10]]

            # Lấy thông tin phim
            results = movies_df[movies_df['id'].isin(top_movie_ids)].copy()

            # Đảm bảo có đủ các cột cần thiết (BẮT BUỘC PHẢI CÓ 'id' và 'overview')
            required_columns = ['id', 'movie_name', 'genres',
                                'director', 'release_year', 'poster_path', 'overview']
            for col in required_columns:
                if col not in results.columns:
                    results[col] = None

            return results[required_columns]

    except Exception as e:
        print(f"❌ Error in get_top_n_recommendations: {e}")
        # Fallback to popular movies
        try:
            return get_top_n_recommendations(user_id, 'new_user', movies_df, None)
        except:
            return pd.DataFrame()


# Hàm helper để format kết quả thành JSON-friendly format
def format_results_for_json(df):
    """
    Chuyển đổi DataFrame thành format phù hợp cho JSON response

    Args:
        df (DataFrame): DataFrame kết quả từ các hàm gợi ý

    Returns:
        list: List các dictionary chứa thông tin phim
    """
    if df is None or df.empty:
        return []

    try:
        # Chuyển đổi thành list of dictionaries
        results = df.to_dict('records')

        # Xử lý các giá trị NaN
        for item in results:
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None

        return results
    except Exception as e:
        print(f"❌ Error in format_results_for_json: {e}")
        return []

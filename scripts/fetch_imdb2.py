import os
from imdb import Cinemagoer

# 1. 저장할 폴더 생성
OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

# 2. IMDB 데이터 수집
ia = Cinemagoer()
movie_id = '0241527'  # 해리 포터와 마법사의 돌
print("Fetching reviews from IMDB...")

# 영화 객체를 먼저 가져온 후 리뷰를 업데이트하는 방식이 가장 안전합니다.
movie = ia.get_movie(movie_id)
ia.update(movie, ['reviews'])

# reviews_data['data']['reviews'] 대신 movie['reviews']를 사용합니다.
review_list = []
if 'reviews' in movie:
    for r in movie['reviews']:
        content = r.get('content')
        if content:
            review_list.append(content)
else:
    print("리뷰를 찾을 수 없습니다. ID를 확인하거나 네트워크를 체크하세요.")

# 실습을 위해 최대 30개만 사용
review_list = review_list[:30]
print(f"Total reviews collected: {len(review_list)}")

# 3. 문서 생성 (10개씩 묶어서 .txt 저장)
for i in range(3):
    start_idx = i * 10
    end_idx = (i + 1) * 10
    chunk = review_list[start_idx : end_idx]
    
    if not chunk:
        break

    combined_text = "\n\n" + "="*50 + "\n\n"
    text_content = combined_text.join(chunk)

    path = f"{OUT_DIR}/hp_reviews_{i+1}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text_content)

    print(f"Saved: {path}")

print("Done.")
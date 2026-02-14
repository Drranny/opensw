import wikipediaapi
import os

# 1. 저장 설정
OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="HarryPotterRAGBot/1.0 (contact: yjjang@cluster03.com)"
)

topics = [
    "Harry Potter (character)",
    "Hogwarts",
    "Albus Dumbledore",
    "Lord Voldemort",
    "Magic in Harry Potter"
]

# 2. 모든 토픽의 텍스트를 하나로 합치기
all_wiki_text = ""
for topic in topics:
    page = wiki.page(topic)
    if page.exists():
        all_wiki_text += f"\n\n=== {topic} ===\n\n" + page.text
        print(f"데이터 로드 완료: {topic}")

# 3. 7개의 파일로 나누기 (harrypotter1_4.txt ~ harrypotter1_10.txt)
total_length = len(all_wiki_text)
chunk_size = total_length // 7  # 7등분

for i in range(7):
    start_idx = i * chunk_size
    # 마지막 파일은 남은 텍스트를 모두 포함
    end_idx = (i + 1) * chunk_size if i < 6 else total_length
    
    chunk_text = all_wiki_text[start_idx:end_idx]
    
    # 파일명 설정 (4번부터 10번까지)
    file_num = i + 4
    filename = f"harrypotter1_{file_num}.txt"
    path = os.path.join(OUT_DIR, filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(chunk_text.strip())
        
    print(f"저장 완료: {filename} (길이: {len(chunk_text)})")

print("\n모든 위키 데이터가 harrypotter1_4.txt ~ 10.txt로 분할 저장되었습니다!")
import requests
from bs4 import BeautifulSoup
import os

# 1. 폴더 준비
OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

# 2. 위키 페이지 데이터 가져오기
url = "https://harrypotter.fandom.com/wiki/List_of_spells"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("해리포터 마법 주문 리스트를 가져오는 중...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 3. 데이터 파싱
spells_content = []
# 주문 이름들이 h3 태그 안의 span에 주로 들어있습니다.
spell_elements = soup.find_all('h3')

for element in spell_elements:
    name = element.get_text().strip()
    
    # 실제 주문 이름인 경우만 처리 (불필요한 섹션 제외)
    if name and len(name) > 1:
        description = ""
        # h3 태그 다음의 문단(p)들을 가져와서 설명으로 합침
        next_node = element.find_next_sibling()
        while next_node and next_node.name not in ['h2', 'h3']:
            if next_node.name == 'p':
                description += next_node.get_text().strip() + " "
            next_node = next_node.find_next_sibling()
        
        if description:
            spells_content.append(f"주문명: {name}\n설명: {description.strip()}\n")

# 4. 하나의 파일로 저장
file_path = os.path.join(OUT_DIR, "hp_spells_list.txt")
with open(file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(spells_content))

print(f"완료! 총 {len(spells_content)}개의 주문이 {file_path}에 저장되었습니다.")
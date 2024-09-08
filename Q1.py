import requests
from bs4 import BeautifulSoup

# PTT 熱門看板的網址
url = 'https://www.ptt.cc/bbs/hotboards.html'

# 請求
response = requests.get(url)

# 剖析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有看板的名稱和 URL
boards = soup.find_all('div', class_='board-name')
for board in boards:
    name = board.text
    link = 'https://www.ptt.cc' + board.find_parent('a')['href']
    print(f'列表名稱: {name}, 網址: {link}')

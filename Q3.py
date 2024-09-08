import requests
from bs4 import BeautifulSoup
import os

# 古騰堡計劃的中文書籍頁面 URL
url = 'https://www.gutenberg.org/browse/languages/zh'

# 請求
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到前200本書的URL
book_links = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and '/ebooks/' in href:
        book_links.append('https://www.gutenberg.org' + href)
    if len(book_links) >= 200:
        break  # 僅抓取前200本書的鏈接

# 清理無效字符的函數防止檔案名錯誤
def clean_filename(filename):
    return "".join([c for c in filename if c.isalnum() or c in ' -_']).strip()

# 定義一個函數來檢查檔案名是否存在如果存在則增加數字
def generate_unique_filename(base_filename):
    counter = 1
    filename = base_filename
    while os.path.exists(f"{filename}.txt"):
        filename = f"{base_filename}({counter})"
        counter += 1
    return filename

# 爬每本書的內容
for book_url in book_links:
    book_response = requests.get(book_url)
    book_soup = BeautifulSoup(book_response.text, 'html.parser')
    
    # 抓書籍標題
    title_tag = book_soup.find('h1')
    if title_tag:
        title = title_tag.text.strip()
    else:
        title = "未知標題"

    # 書名作為檔案名
    clean_title = clean_filename(title)
    
    # 檔案名如果同名則加上數字
    unique_filename = generate_unique_filename(clean_title)
    
    # 抓取作者信息
    author_tag = book_soup.find('a', {'itemprop': 'creator'})
    author = author_tag.text.strip() if author_tag else "未知作者"
    
    # 抓取發行日期（有時會沒有）
    release_date_tag = book_soup.find('th', text='Release Date')
    release_date = release_date_tag.find_next_sibling('td').text.strip() if release_date_tag else "未知發行日期"

    # 抓取書籍的內文通常會在 Plain Text UTF-8 這類鏈接下
    text_url = None
    for link in book_soup.find_all('a'):
        if 'Plain Text UTF-8' in link.text:
            text_url = 'https://www.gutenberg.org' + link['href']
            break

    if text_url:
        text_response = requests.get(text_url)
        book_content = text_response.text
    else:
        book_content = "無法抓取內文"

    # 將書籍的資料寫入，使用唯一檔案名
    with open(f"{unique_filename}.txt", "w", encoding="utf-8") as f:
        f.write(f"書名: {title}\n")
        f.write(f"作者: {author}\n")
        f.write(f"發行日期: {release_date}\n")
        f.write(f"內文:\n{book_content}\n")
    
    print(f'已成功抓取 "{title}" 並儲存為 {unique_filename}.txt')


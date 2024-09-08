import requests
from bs4 import BeautifulSoup
import re
import os

# 八卦版的 URL
url = 'https://www.ptt.cc/bbs/Gossiping/index.html'

# 加上 cookies 繞過年齡驗證
cookies = {'over18': '1'}

# 請求並剖析頁面
response = requests.get(url, cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有貼文
posts = soup.find_all('div', class_='r-ent')

# 定義清理無效字串的函數
def clean_filename(filename):
    return re.sub(r'[\/:*?"<>|]', "", filename)

for post in posts:
    title_tag = post.find('a')
    if title_tag:
        title = title_tag.text
        clean_title = clean_filename(title)  # 清理無效字符的標題作為檔案名

        # 檢查該文章是否已經保存過
        if os.path.exists(f"{clean_title}.txt"):
            print(f'已成功抓取 "{title}" 並跳過此篇文章')
            continue  # 檔案已存在，跳過該文章

        post_url = 'https://www.ptt.cc' + title_tag['href']
        
        # 進入貼文
        post_response = requests.get(post_url, cookies=cookies)
        post_soup = BeautifulSoup(post_response.text, 'html.parser')

        # 作者、時間、內文
        meta_data = post_soup.find_all('span', class_='article-meta-value')

        if len(meta_data) >= 4:
            author = meta_data[0].text
            post_time = meta_data[3].text
            content = post_soup.find(id='main-content').text

            # 貼文資料保存
            with open(f"{clean_title}.txt", "w", encoding="utf-8") as f:
                f.write(f"作者: {author}\n")
                f.write(f"標題: {title}\n")
                f.write(f"發文時間: {post_time}\n")
                f.write(f"內文: {content}\n")

            # 留言
            comments = post_soup.find_all('div', class_='push')
            for comment in comments:
                comment_author = comment.find('span', class_='f3 hl push-userid').text
                comment_content = comment.find('span', class_='f3 push-content').text
                comment_time = comment.find('span', class_='push-ipdatetime').text.strip()
                
                # 留言存到同一個檔案中
                with open(f"{clean_title}.txt", "a", encoding="utf-8") as f:
                    f.write(f"留言者: {comment_author}\n")
                    f.write(f"留言時間: {comment_time}\n")
                    f.write(f"留言內容: {comment_content}\n")
            
            # print成功
            print(f'已成功抓取 "{title}" 並儲存為 {clean_title}.txt')
        else:
            print(f"無法提取作者或發文時間: {post_url}")

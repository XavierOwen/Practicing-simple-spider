import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "https://www.newadvent.org/"

def html_to_markdown(paragraph, base_url):
    # 替换斜体
    for i_tag in paragraph.find_all('i'):
        i_tag.insert_before("*")
        i_tag.insert_after("*")
        i_tag.unwrap()
    # 替换粗体
    for b_tag in paragraph.find_all('b'):
        b_tag.insert_before("**")
        b_tag.insert_after("**")
        b_tag.unwrap()
    # 替换超链接为完整 URL
    for a_tag in paragraph.find_all('a'):
        href = a_tag.get('href', '')
        if href.startswith("#"):
            a_tag.unwrap()  # 丢弃锚点链接
            continue
        full_url = urljoin(base_url, href)
        text = a_tag.get_text()
        a_tag.replace_with(f"[{text}]({full_url})")
    return paragraph.get_text(strip=False)

def fetch_all_to_one_md(start=1, end=124, output_file='fathers.md'):
    all_md_lines = []

    for i in range(start, end + 1):
        page_url = f"https://www.newadvent.org/fathers/1701{i:03d}.htm"
        print(f"📥 Fetching: {page_url}")
        try:
            response = requests.get(page_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Failed to fetch {page_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取 <h1> 标题
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else f"Article {i}"
        all_md_lines.append(f"## {title}")

        # 提取 <p> 并跳过第一个
        paragraphs = soup.find_all('p')
        for p in paragraphs[1:]:
            md_line = html_to_markdown(p, base_url=page_url)
            if md_line.strip():
                all_md_lines.append(md_line)

        # 分隔线
        all_md_lines.append("\n---\n")
        time.sleep(5)

    # 写入 Markdown 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(all_md_lines))

    print(f"\n✅ All {end-start+1} articles saved to '{output_file}'.")

if __name__ == '__main__':
    fetch_all_to_one_md()
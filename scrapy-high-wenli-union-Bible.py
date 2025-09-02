import requests
from bs4 import BeautifulSoup, Tag

# titles
# Target URL
url = "https://zh.wikisource.org/wiki/%E8%81%96%E7%B6%93_(%E6%96%87%E7%90%86%E5%92%8C%E5%90%88)"

# Fetch the page
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Filtered extraction
book_titles = []
for li in soup.find_all("li"):
    a_tag = li.find("a")
    if a_tag and a_tag.has_attr("href"):
        if a_tag["href"].startswith("/wiki/%E8%81%96%E7%B6%93") or \
           a_tag["href"].startswith("https://zh.wikisource.org/wiki/%E8%81%96%E7%B6%93"):
            book_titles.append(a_tag.get_text(strip=True))

book_titles = book_titles[3:]

url = "https://zh.wikisource.org/zh-hans/%E8%81%96%E7%B6%93_(%E6%96%87%E7%90%86%E5%92%8C%E5%90%88)"
# Fetch the page
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Filtered extraction
book_titles_s = []
for li in soup.find_all("li"):
    a_tag = li.find("a")
    if a_tag and a_tag.has_attr("href"):
        if a_tag["href"].startswith("/wiki/%E8%81%96%E7%B6%93") or \
           a_tag["href"].startswith("https://zh.wikisource.org/wiki/%E8%81%96%E7%B6%93"):
            book_titles_s.append(a_tag.get_text(strip=True))

book_titles_s = book_titles_s[3:]

# Container for extracted content
results = []

for i, book_title in enumerate(book_titles):
    #chapter_title = "#" + book_titles_s[i]
    results.append(f"# {book_titles_s[i]}")
    url = "https://zh.wikisource.org/zh-hans/%E8%81%96%E7%B6%93_(%E6%96%87%E7%90%86%E5%92%8C%E5%90%88)/"+book_title
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    # Walk through elements in document order
    for elem in soup.body.descendants:
        if isinstance(elem, Tag):
            # Handle headings
            if elem.name == 'h2':
                heading_text = elem.get_text(strip=True)
                if heading_text:
                    #results.append("\n## " + heading_text+"\n")
                    results.append(f"\n## {heading_text}\n")
            # Paragraphs with verse numbers
            elif elem.name == "p":
                sup = elem.find("sup")
                text = elem.get_text(strip=True)
                if text:
                    if sup:
                        number = sup.get_text(strip=True)
                        # Remove the number from text body
                        text = text.replace(number, "", 1).strip()
                        if text.endswith("、○"):
                            text = text[:-2] + "。"
                        results.append(f"{number} {text}")
                    else:
                        if text.endswith("、○"):
                            text = text[:-2] + "。"
                        results.append(text)
    results.append('\n')

text_output = "\n".join(results)
#print(text_output)

# Optionally write to file
with open("bible.txt", "w", encoding="utf-8") as f:
    f.write(text_output)

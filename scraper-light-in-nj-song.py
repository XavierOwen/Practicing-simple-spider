import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from urllib.parse import urljoin
import re
import time
import random

BASE_URL = "http://www.lightinnj.org/%E5%B1%9E%E7%81%B5%E4%B9%A6%E6%8A%A5/004%E8%AF%BB%E7%BB%8F%E7%B1%BB%20%E7%9B%AE%E5%BD%95/4004%E6%AD%8C%E4%B8%AD%E7%9A%84%E6%AD%8C/%E6%AD%8C%E4%B8%AD%E7%9A%84%E6%AD%8C%20%20%E7%9B%AE%E5%BD%95.htm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch_html(url: str) -> str:
    """Fetch HTML and handle encoding"""
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.encoding = "gb18030"  # lightinnj uses GB18030 encoding
    # Polite delay
    time.sleep(random.uniform(0.5, 1.5))
    return r.text

def extract_links_from_index(html: str, base_url: str) -> list[tuple[str, str]]:
    """Extract section titles and links from the index page"""
    soup = BeautifulSoup(html, "html.parser")

    links = []
    anchors = soup.find_all("a", href=True)

    for a in anchors:
        text = a.get_text(strip=True)
        href = a.get("href")

        # Skip navigation links
        if text in ["回首页"]:
            continue

        # Only get actual section links (not too long)
        if href and not href.startswith("../") and text:
            full_url = urljoin(base_url, href)
            links.append((text, full_url))

    return links

def extract_page_content(html: str) -> str:
    """Extract main text and treat <b> blocks as headings.

    - Skips navigation like 书名/回目录
    - Works for 导言 where multiple <b> (一..八) appear in one <p>
    - Works for sections with headings like 壹 羡慕（一章二至三节）
    - Converts <br> tags to paragraph breaks (\n\n) for Markdown
    - Treats <b> that start with simplified numerals followed by fullwidth space (一二三…＋\u3000) as level-4 (####)
    """
    soup = BeautifulSoup(html, "html.parser")

    lines: list[str] = []
    current_heading: str | None = None
    current_heading_level: int = 3
    buffer: list[str] = []

    def flush_buffer():
        nonlocal buffer, current_heading, current_heading_level
        # Join buffer and preserve intentional paragraph breaks from <br>
        text = "".join(buffer).strip()
        buffer.clear()
        if not text:
            return
        if current_heading:
            lines.append(f"{'#' * current_heading_level} {current_heading}")

        # Split by double newlines (from <br><br>) first to preserve paragraph structure
        paragraphs = re.split(r"\n\n+", text)

        cleaned_paragraphs = []
        for para in paragraphs:
            # Within each paragraph, normalize whitespace but preserve single line breaks
            para_lines = para.split("\n")
            cleaned_lines = []
            for line in para_lines:
                # Normalize whitespace within each line
                cleaned = re.sub(r"[ \t]+", " ", line).strip()
                if cleaned:
                    cleaned_lines.append(cleaned)

            # Rejoin lines within paragraph
            para_text = "\n".join(cleaned_lines).strip()
            if para_text:
                cleaned_paragraphs.append(para_text)

        # Join paragraphs with double newlines (Markdown paragraph separator)
        text = "\n\n".join(cleaned_paragraphs)
        lines.append(text)

    # Iterate all <p> in order; inside each, walk children to split by <b>
    # regex to identify H4 headings that begin with simplified Chinese numerals followed by a fullwidth space
    h4_simplified_re = re.compile(r"^[一二三四五六七八九十]+\u3000")

    for p in soup.find_all("p"):
        # quick navigation skip
        p_text = p.get_text(strip=True)
        if not p_text:
            continue
        if p_text.startswith("回目录") or p_text.startswith("书名："):
            continue

        for node in p.children:
            if isinstance(node, Tag):
                name = (node.name or "").lower()
                if name == "b":
                    # heading inside this paragraph
                    heading = node.get_text(strip=True)
                    if heading and not heading.startswith("书名") and not heading.startswith("回目录"):
                        flush_buffer()
                        # classify heading level: default H3, but if starts with simplified numerals + fullwidth space, use H4
                        if h4_simplified_re.match(heading):
                            current_heading_level = 4
                        else:
                            current_heading_level = 3
                        current_heading = heading
                    # do not add <b> text to buffer
                    continue
                elif name == "br":
                    # Convert <br> to paragraph break (\n\n) in Markdown
                    buffer.append("\n\n")
                    continue
                else:
                    # add tag's text with spaces preserved
                    t = node.get_text(separator=" ", strip=True)
                    if t:
                        buffer.append(t)
                        buffer.append(" ")
            elif isinstance(node, NavigableString):
                t = str(node).strip()
                if t:
                    buffer.append(t)
                    buffer.append(" ")

    # flush remaining
    flush_buffer()

    # Compose markdown
    md = "\n\n".join(lines).strip()
    return md

def build_book_markdown() -> str:
    """Build the complete markdown document"""
    index_html = fetch_html(BASE_URL)
    links = extract_links_from_index(index_html, BASE_URL)

    lines = []
    lines.append("# 歌中之歌\n")

    def dedup_leading_title(content: str, title: str) -> str:
        """Remove a leading line that duplicates the section title.

        Compares after normalizing fullwidth spaces to normal spaces and collapsing
        whitespace. Also ignores leading Markdown hashes on the first line.
        """
        def canon(s: str) -> str:
            s = s.replace("\u3000", " ")
            s = re.sub(r"\s+", " ", s).strip()
            return s

        content = content.lstrip()
        m = re.match(r"^(.*?)(\n|$)", content, re.S)
        if not m:
            return content
        first_line = m.group(1).strip()
        # strip heading hashes if present
        first_line_no_hash = re.sub(r"^#+\s+", "", first_line)
        if canon(first_line_no_hash) == canon(title):
            # drop the first line and following newline
            return content[len(m.group(0)):] .lstrip("\n")
        return content

    for section_title, section_url in links:
        print(f"Scraping: {section_title}")

        try:
            page_html = fetch_html(section_url)
            content = extract_page_content(page_html)
            # Remove duplicated inline title inside the content if present
            content = dedup_leading_title(content, section_title)

            if content:
                lines.append(f"## {section_title}\n")
                lines.append(content)
                lines.append("")
        except Exception as e:
            print(f"  ⚠️ Error scraping {section_title}: {e}")

    # Join all lines and clean up
    md = "\n".join(lines).strip()
    # Normalize: replace fullwidth space with normal space and remove normal space after ideographic full stop
    md = md.replace("\u3000", " ")
    md = re.sub(r"。 +", "。", md)
    # Remove excessive blank lines
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md + "\n"

if __name__ == "__main__":
    md = build_book_markdown()
    filename = "歌中之歌.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ 已生成：{filename}")

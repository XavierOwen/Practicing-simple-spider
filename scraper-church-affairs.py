import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from urllib.parse import urljoin
import re
import time
import random

BASE_URL = "https://ezoe.work/books/3/3007.html"
BASE_PATH = "https://ezoe.work/books/3/3007"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch_html(url: str) -> str:
    """Fetch HTML and handle encoding"""
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.encoding = "utf-8"
    # Polite delay to avoid overwhelming the server
    time.sleep(random.uniform(0.5, 1.5))
    return r.text

def extract_chapters_from_index(html: str) -> list[tuple[str, str]]:
    """Extract chapter titles and links from the index page (3007.html)

    Returns list of tuples: (chapter_title, chapter_url)
    """
    soup = BeautifulSoup(html, "html.parser")
    chapters = []

    # Find all links in the page
    anchors = soup.find_all("a", href=True)

    for a in anchors:
        if not isinstance(a, Tag):
            continue
        href_raw = a.get("href", "")
        if isinstance(href_raw, list):
            # If BeautifulSoup returns a list (e.g., AttributeValueList), join its parts
            href = ' '.join(href_raw)
        else:
            # Otherwise, it's a string, so just use it
            href = href_raw
        href = href.strip()
        text = a.get_text(strip=True)

        # Look for links matching pattern 3007-1.html, 3007-2.html, etc.
        if href and re.match(r"3007-\d+\.html", href):
            full_url = urljoin(BASE_URL, href)
            chapters.append((text, full_url))

    return chapters

def extract_section_heading_from_start(html: str) -> str:
    """Extract the main chapter title (e.g., '教会里的职分') without the 第X篇 prefix

    This appears at the beginning of each chapter page after navigation.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Find the feature-title div which contains the chapter heading
    feature_title = soup.find('div', class_='feature-title')
    if feature_title:
        text = feature_title.get_text(strip=True)
        # Remove "第X篇" prefix if present (with or without space)
        text = re.sub(r'^第[^篇]+篇\s*', '', text)
        return text.strip()

    # Fallback: search in all text
    text_content = soup.get_text()
    match = re.search(r'第[^篇]+篇\s*([^\n]+)', text_content)
    if match:
        return match.group(1).strip()

    return ""

def extract_page_content(html: str) -> str:
    """Extract main content from a chapter page.

    Converts HTML structure to Markdown:
    - <div class='main'> contains the actual content
    - <div class='cn1'> contains H3 section markers (壹, 贰, etc.)
    - <div class='cn2'> contains H4 subsection markers
    - Plain <div> or <div class='cont'> contain the content paragraphs
    - Preserves paragraph breaks
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the main content container
    main_div = soup.find('div', class_='main')
    if not main_div:
        # Fallback to id='c' if main div not found
        main_div = soup.find(id='c')

    if not main_div:
        return ""

    lines: list[str] = []

    # Process all children of the main content div
    for child in main_div.children:
        if not isinstance(child, Tag):
            continue

        # Skip <br> tags
        if child.name == 'br':
            continue

        # Check if this is a cn1 section heading (H3)
        if child.has_class('cn1'):
            heading_text = child.get_text(strip=True)
            lines.append(f"\n### {heading_text}\n")

        # Check if this is a cn2 subsection heading (H4)
        elif child.has_class('cn2'):
            heading_text = child.get_text(strip=True)
            lines.append(f"\n#### {heading_text}\n")

        # Otherwise, this is a content paragraph
        elif child.name == 'div':
            # Extract text content, handling nested tags
            content_parts = []

            for elem in child.descendants:
                if isinstance(elem, NavigableString):
                    text = str(elem).strip()
                    if text:
                        content_parts.append(text)
                elif isinstance(elem, Tag) and elem.name == 'br':
                    content_parts.append(' ')

            # Join and clean the content
            content = ' '.join(content_parts)
            content = re.sub(r'\s+', ' ', content).strip()

            if content:
                lines.append(content)
                lines.append("")  # Add paragraph break

    # Join lines and clean up excessive spacing
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    return md

def build_book_markdown() -> str:
    """Build the complete markdown book"""
    print("📖 Fetching index page...")
    html_index = fetch_html(BASE_URL)
    chapters = extract_chapters_from_index(html_index)

    print(f"✅ Found {len(chapters)} chapters")

    out = []
    out.append("# 教会的事务\n")

    for idx, (chapter_title, chapter_url) in enumerate(chapters, start=1):
        print(f"📄 Processing chapter {idx}/{len(chapters)}: {chapter_title}")

        # Fetch chapter page
        chapter_html = fetch_html(chapter_url)

        # Extract section heading
        section_heading = extract_section_heading_from_start(chapter_html)
        if section_heading:
            out.append(f"## {section_heading}\n")

        # Extract main content
        content = extract_page_content(chapter_html)

        if content:
            out.append(content + "\n")

        # Add link to original
        out.append(f"[原文链接]({chapter_url})\n")
        out.append("")

    return "\n".join(out).strip() + "\n"

if __name__ == "__main__":
    print("🚀 Starting scraper for '教会的事务'...\n")
    md = build_book_markdown()

    output_file = "教会的事务.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n✅ Successfully generated: {output_file}")

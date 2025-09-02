import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin
import re

BASE_URL = "https://pages.uoregon.edu/fyin/%E7%81%B5%E7%B2%AE/%E5%8D%81%E4%BA%8C%E7%AF%AE/%E5%8D%81%E4%BA%8C%E7%AF%AE%20%E7%9B%AE%E5%BD%95.htm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

CN_NUM = ["第一辑","第二辑","第三辑","第四辑","第五辑","第六辑","第七辑","第八辑","第九辑","第十辑","第十一辑","第十二辑"]

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.encoding = "gb18030"  # 该站点国标编码
    return r.text

def extract_main_links(html: str, base_url: str) -> list[str]:
    """目录页：提取 12 个一级链接（注意你此前的 1:14 切片修正）"""
    soup = BeautifulSoup(html, "html.parser")
    table3 = soup.find(id="table3")
    if not table3:
        table3 = soup.select_one('#table3, a[name="table3"], [name="table3"]')
        if table3 and table3.name == "a":
            table3 = table3.parent
    anchors = table3.find_all("a", href=True)
    anchors = [a for a in anchors if not a["href"].startswith("#")]
    anchors = anchors[1:14]  # 你修过的范围
    return [urljoin(base_url, a["href"]) for a in anchors]

def extract_sub_anchors(html: str):
    """子页：返回 12 个 <a> 标签（对象），用于拿标题文本和链接"""
    soup = BeautifulSoup(html, "html.parser")
    td = soup.find("td", attrs={"colspan": "5"})
    if not td:
        td = soup.find("td", attrs={"colspan": "4"})
    if not td:
        return []
    anchors = td.find_all("a", href=True)
    return anchors[:12]

def anchor_title_after_dunhao(text: str) -> str:
    """从锚文本中取“顿号”后的标题；若无顿号，返回原文本"""
    t = (text or "").strip()
    if "、" in t:
        parts = t.split("、", 1)
        # 若顿号在最前或分割后为空，退回原文本
        cand = parts[1].strip()
        return cand or t
    return t

def third_p_to_markdown(html: str) -> str:
    """取第三个 <p>，把里面的 <b> 转成 #### 标题；其他按纯文本处理，<br> 转换为换行。"""
    soup = BeautifulSoup(html, "html.parser")
    p_list = soup.find_all("p")

    # 选择“可见文本长度”最大的 <p> 作为正文段落；把 <br> 当作换行
    candidates = [p for p in p_list if p.get_text(strip=True)]
    if not candidates:
        return ""

    def _text_len(p: Tag) -> int:
        return len(p.get_text(separator="\n", strip=True))

    target = max(candidates, key=_text_len)

    lines = []
    buf = []

    def flush_buf_as_text():
        text = "".join(buf)
        if not text:
            buf.clear()
            return
        # 统一换行
        text = re.sub(r"\r\n?", "\n", text)
        # 去除每行行首多余缩进（普通空格 / 制表符 / 不换行空格 / 全角空格）
        cleaned_lines = [re.sub(r'^[\u3000\u00A0 \t]+', '', ln) for ln in text.split('\n')]
        text_clean = "\n".join(cleaned_lines).strip()
        if text_clean:
            lines.append(text_clean)
        buf.clear()

    # 遍历 target 的直接/嵌套子节点，处理 <b>、<br> 等
    for node in target.descendants:
        if isinstance(node, NavigableString):
            # 如果该文本节点属于 <b> 内部，则跳过，避免将 <b> 内容既作为标题又重复为正文
            parent = getattr(node, 'parent', None)
            if isinstance(parent, Tag) and parent.name and parent.name.lower() == 'b':
                continue
            buf.append(str(node))
        elif isinstance(node, Tag):
            if node.name.lower() == "br":
                buf.append("\n")
            elif node.name.lower() == "b":
                # 输出之前的缓冲文本为段落
                flush_buf_as_text()
                title = node.get_text(strip=True)
                if title:
                    lines.append(f"#### {title}")
                # <b> 内文本不再重复追加
            else:
                # 其他标签按其纯文本加入缓冲（避免重复抓取其孩子）
                # 但 descendants 会再到其子节点，这里跳过以免重复；
                # 让 NavigableString 分支处理子文本即可
                pass

    # 收尾
    flush_buf_as_text()

    # 规范化：把多余空行压缩为两行
    md = "\n\n".join([s.strip() for s in lines if s is not None])
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md

def build_book_markdown() -> str:
    html_main = fetch_html(BASE_URL)
    main_links = extract_main_links(html_main, BASE_URL)
    if len(main_links) != 12:
        print(f"⚠️ 一级链接数量={len(main_links)}（预期 12），将按实际处理。")

    out = []
    out.append("# 十二篮\n")

    for vol_idx, vol_url in enumerate(main_links, start=1):
        vol_name = CN_NUM[vol_idx - 1] if vol_idx - 1 < len(CN_NUM) else f"第{vol_idx}辑"
        out.append(f"## {vol_name}\n")

        sub_html = fetch_html(vol_url)
        anchors = extract_sub_anchors(sub_html)

        # 若不足 12 个锚点，按实际数量写
        for a in anchors:
            title_full = a.get_text(" ", strip=True)
            title = anchor_title_after_dunhao(title_full) or title_full
            link = urljoin(vol_url, a["href"])

            # 抓内容页的第三个 <p>
            page_html = fetch_html(link)
            body_md = third_p_to_markdown(page_html)

            # 写入一个条目
            out.append(f"### {title}\n")
            # 可在标题下放原文链接（可选）
            out.append(f"[原文链接]({link})\n")
            if body_md:
                out.append(body_md + "\n")
            else:
                out.append("_（本条未检测到第三个段落或内容为空）_\n")

        # 分卷之间加一行
        out.append("")

    return "\n".join(out).strip() + "\n"

if __name__ == "__main__":
    md = build_book_markdown()
    with open("十二篮.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("✅ 已生成：十二篮.md")
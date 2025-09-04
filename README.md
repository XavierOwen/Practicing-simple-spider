# 一些个人实现的网页内容抓取器

Python 脚本抓取并转换为 Markdown。

```bash
git clone https://github.com/XavierOwen/Practicing-simple-spider.git
cd Practicing-simple-spider
pip install -r requirements.txt
```

转换pdf最好使用npm的markdown-pdf，以生成可以使用的书签和超链接。

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node
npm i -g md-to-pdf
```

vscode插件Markdown All in One可以自动生成目录在markdown文件内

## 十二篮

[原文链接](https://pages.uoregon.edu/fyin/%E7%81%B5%E7%B2%AE/%E5%8D%81%E4%BA%8C%E7%AF%AE/%E5%8D%81%E4%BA%8C%E7%AF%AE%20%E7%9B%AE%E5%BD%95.htm)

```bash
python scraper-12-brackets.py
python clean-12-brackets.py "十二篮.md" --inplace
md-to-pdf 十二篮.md --config-file md2pdf.json
```

## 深文理和合本

[原文链接](https://zh.wikisource.org/zh-hans/%E8%81%96%E7%B6%93_(%E6%96%87%E7%90%86%E5%92%8C%E5%90%88))

```bash
python scraper-high-wenli-union-Bible.py
```

## 约翰福音讲道录

[原文链接](https://www.newadvent.org/fathers/1701.htm)

```bash
python scraper-lectures-on-the-Gospel-of-John.py
```
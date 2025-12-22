# 一些个人实现的网页内容抓取器

Python 脚本抓取并转换为 Markdown。

```bash
git clone https://github.com/XavierOwen/Practicing-simple-spider.git
cd Practicing-simple-spider
pip install -r requirements.txt
```

转换pdf最好使用npm的markdown-pdf，以生成可以点击跳转的**书签**。

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node
npm i -g md-to-pdf
```

vscode插件Markdown All in One可以自动生成目录在markdown文件，建议放在heading 1下方，方便读者回到首页点击链接，而不是从pdf阅读器提供的书签功能再去跳转。

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

## 马太福音查经记录

[原文链接](http://lightinnj.org/%E5%80%AA%E6%9F%9D%E8%81%B2%E6%96%87%E9%9B%86/%E5%80%AA%E6%9F%9D%E8%81%B2%E6%96%87%E9%9B%86%E7%AC%AC%E4%B8%80%E8%BE%91/15%E9%A9%AC%E5%A4%AA%E7%A6%8F%E9%9F%B3%E6%9F%A5%E7%BB%8F%E8%AE%B0%E5%BD%95/%E9%A9%AC%E5%A4%AA%E7%A6%8F%E9%9F%B3%E6%9F%A5%E7%BB%8F%E8%AE%B0%E5%BD%95%E7%9B%AE%E5%BD%95.htm)

```bash
python python scraper-Mattew-Study-Nee.py
md-to-pdf 马太福音查经记录.md --config-file md2pdf.json
```
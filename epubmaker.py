from ebooklib import epub
from progressbar import *
import os


class EpubMaker:
    def __init__(self):
        self.catalog = []
        self.identifier = 'Default'
        self.title = 'Default'
        self.language = 'zh_Hans'
        self.author = 'Default'
        self.toc = []
        self.content = []
        self.nums = 0
        self.book = None
        self.output_path='Default'
        self.output_name = 'Default'

    def set_arg(self, title, author, content, catalog, num, output_path, language='zh_Hans'):
        self.title = title
        self.author = author
        self.language = language
        self.content = content
        self.catalog = catalog
        self.nums = num
        self.output_name = title + '.epub'
        self.output_path=output_path

    def run(self):
        self.book = epub.EpubBook()
        self.book.set_identifier(self.identifier)
        self.book.set_language(self.language)
        self.book.set_title(self.title)
        self.book.add_author(self.author)

        copyright = epub.EpubHtml(title="版权声明", file_name="copyright.html")
        copyright.content = """<h1>版权声明</h1>
        <p>本工具目的是将免费网络在线小说转换成方便kindle用户阅读的mobi电子书, 作品版权归原作者或网站所有, 请不要将该工具用于非法用途。</p>
        """
        self.book.add_item(copyright)
        self.toc.append(epub.Link("copyright.html", "版权声明", "intro"))

        volume = []
        pb = ProgressBar()
        for i in pb(range(self.nums)):
            ch_name = self.catalog[i]
            chapter = epub.EpubHtml(title=ch_name, file_name='ch{}.html'.format(i))
            chapter.set_content(u"<h1>" + ch_name + u"</h1>" + self.content[i])
            self.book.add_item(chapter)
            volume.append(chapter)

        self.toc.append((epub.Section('正文'), volume))
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)
        # basic spine
        self.book.spine = [copyright]
        self.book.spine.extend(volume)

        self.book.toc = self.toc
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        epub.write_epub(os.path.join(self.output_path, self.output_name), self.book)

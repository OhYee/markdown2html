import unittest
from markdown import render_markdown


class TestMarkdown(unittest.TestCase):
    def test_code(self):
        inp = '`code`'
        exp = '<code>code</code>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_image(self):
        inp = "![OhYee's Blog](https://www.oyohyee.com/logo.svg)"
        exp = '<a href="https://www.oyohyee.com/logo.svg" alt="OhYee\'s&nbsp;Blog" data-lightbox="OhYee\'s&nbsp;Blog-https://www.oyohyee.com/logo.svg" data-title="OhYee\'s&nbsp;Blog"><img class="img-responsive" src="https://www.oyohyee.com/logo.svg" alt="OhYee\'s&nbsp;Blog"></a>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_link(self):
        inp = "[OhYee's Blog](https://www.oyohyee.com/)"
        exp = '<a href="https://www.oyohyee.com/">OhYee\'s&nbsp;Blog</a>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_autolink(self):
        inp = 'https://www.oyohyee.com/'
        exp = '<a href="https://www.oyohyee.com/">https://www.oyohyee.com/</a>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_em(self):
        inp = '*em*'
        exp = '<em>em</em>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_strong(self):
        inp = '**strong**'
        exp = '<strong>strong</strong>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_mix_inline(self):
        inp = "`**code**` **[OhYee's Blog](https://www.oyohyee.com/)**"
        exp = '<code>**code**</code> <strong><a href="https://www.oyohyee.com/">OhYee\'s&nbsp;Blog</a></strong>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_codeblock(self):
        inp = '''```python
print("hello")
```'''
        exp = '<pre class="codeblock"><codeblock class="python">print("hello")</codeblock></pre>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_li(self):
        inp = '''- 1
- 2
  - 2.1
  - 2.2
  2 string
- 3
'''
        exp = '<ul class="browser-default"><li>1</li><li>2<br><ul class="browser-default"><li>2.1</li><li>2.2</li>2 string<br></ul></li><li>3</li></ul>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_table(self):
        inp = '''|first|second|third|
|:---:|:---|---:|
|1.1|1.2|1.3|
|2.1|2.2|2.3|'''
        exp = '<table class="responsive-table highlight striped"><tr><td class="center" >first</td><td class="left" >second</td><td class="right" >third</td></tr><tr><td class="center" >1.1</td><td class="left" >1.2</td><td class="right" >1.3</td></tr><tr><td class="center" >2.1</td><td class="left" >2.2</td><td class="right" >2.3</td></tr></table>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)

    def test_blockquote(self):
        inp = '''> blockquote'''
        exp = '<blockquote>blockquote</blockquote>'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)
    
    def test_escape(self):
        inp = r'\q \`code`'
        exp = 'q `code`'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)
    
    def test_math(self):
        inp = r'$\int$'
        exp = r'$\int$'
        oup = render_markdown(inp)
        self.assertEqual(exp, oup)


if __name__ == "__main__":
    unittest.main()

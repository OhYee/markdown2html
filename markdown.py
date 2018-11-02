def render_markdown(raw: str, allow_html: bool = True, debug: bool = False)->str:
    '''
    Render markdown to HTML.
    '''

    import re
    import sys
    import time
    import hashlib

    # log
    def log(indent: int, *args):
        '''
        Output debug log if `debug = True`.
        '''
        nonlocal debug
        if not debug:
            return

        frame = sys._getframe(1)
        func_name = frame.f_code.co_name
        # func_args = frame.f_locals
        func_line = frame.f_lineno

        # func_args = ", ".join(["=".join(map(str, item))
        #    for item in func_args.items()])

        if type(indent) != int:
            args = [indent] + list(args)
            indent = 0
            f = frame
            while f.f_back != None:
                f = f.f_back
                indent += 1

        # if len(func_args) > 0:
            # func_args = func_args[:0]+'...'

        def printl(*args):
            print("  " * indent, *args)

        printl("="*3, "{}():{}".format(func_name, func_line), "="*3)
        printl(*args)

    # line
    tid = 0
    holders = {}
    uniqid = hashlib.md5(str(time.time()).encode()).hexdigest()

    line_grammer_list = [
        # raw
        [r'\{\% raw \%\}(.*?)\{\% endraw \%\}',r'\1'],
        # code
        [r'(?<!\\)`(.+?)`', r'<code>\1</code>'],
        # image
        [r'(?<!\\)\!\[(.*?)\]\((.*?)\)',
            r'<a href="\2" alt="\1" data-lightbox="\1-\2" data-title="\1"><img class="img-responsive" src="\2" alt="\1"></a>'],
        # link
        [r'(?<!\\)\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'],
        # auto link
        [r'<{0,1}((?:ht|f)t(?:p|ps)://[\w\-\.\_,@?^=%&:~\+#\/]+)>{0,1}',
         r'<a href="\1">\1</a>'],
        # strong
        [r'(?<!\\)[_\*]{2}(.*?)[_\*]{2}', r'<strong>\1</strong>'],
        # em
        [r'(?<!\\)[_\*](.*?)[_\*]', r'<em>\1</em>'],
        # title
        [r'(?<!\\)(?<!#)(#+) (.*)\s*$', lambda res: r'<h' + \
            str(len(res[1])) + r'>' + res[2] + '</h' + str(len(res[1])) + '>'],
        # checkbox
        [r'(?<!\\)\[([xX ])\] (.*?)$', lambda res: r'<input type="checkbox" disabled="disabled"' + \
            (r' checked="checked"' if res[1] != ' ' else '') + r'>' + res[2]],
        # hrs
        [r'^-{3,}$', '<hr>'],
        # escape
        # [r'(?:\\(.))', r'\1'],
    ]

    def make_holder(text: str)->str:
        '''
        Make a holder, providing to parse repeatly.
        '''
        nonlocal uniqid, tid, holders
        key = '|\r' + str(uniqid) + str(tid) + '\r|'
        tid += 1
        holders[key] = text
        return key

    def release_holder(text: str)->str:
        '''
        Release the holder.
        '''
        nonlocal holders

        result = re.findall('(\|\r.+?\r\|)', text)
        log(result)
        while result:
            for key in result:
                log("release {}".format(key.replace('\r', '\\r')))
                text = text.replace(key, holders[key])
                del holders[key]
                log("holders {}".format(str(holders)))
            result = re.findall('(\|\r.+?\r\|)', text)

        # for key in holders.keys():
        #     text = text.replace(key, holders[key])
        # holders = {}
        return text

    def encode_html(text: str, space=True):
        '''
        Solve the special character.
        '''
        text = text.replace('&', '&amp;').replace('"', '&quot;')
        if space == True:
            text = text.replace(' ', '&nbsp;')
        return text

    def format_text(fmt: "str or function", groups: list):
        '''
        Output the string as format.
        '''
        text = ""
        res = [escape_html(encode_html(match)) for match in groups]
        res.insert(0, "")
        log(res,fmt)
        if type(fmt) == str:
            text = fmt
            result = re.findall(r'\\([0-9]+)', text)
            for i in set(result):
                text = text.replace('\\'+i, res[int(i)])
        else:
            text = fmt(res)
        return text

    def parse_line(line: str)->str:
        '''
        Parse line.
        '''
        log(line)
        for line_type in line_grammer_list:
            line = re.sub(line_type[0], lambda matches: make_holder(
                format_text(line_type[1], matches.groups())), line, flags=re.M)
        log(str(holders))
        line = re.sub(r'\\(.)', r'\1', line)
        line = release_holder(line).strip()
        log(str(line))
        return line

    # block
    block_grammer_list = []

    def block(block_regex: str, block_end_regex: str):
        '''
        Mark this is a block render function.
        '''
        def outer(func):
            def inner(*args, **kwargs):
                log("Block in.", func.__name__)
                return func(*args, **kwargs)
            block_grammer_list.append((block_regex, block_end_regex, inner))
            return inner
        return outer

    def find_first(line: str)->int:
        '''
        Find the first non-blank charister.
        '''
        pos = -1
        for (idx, char) in enumerate(line):
            if char != ' ':
                pos = idx
                break
        return pos

    def delete_space(lines: list)->list:
        '''
        Delete space in the line front.
        '''
        Minpos = 9999999999
        for line in lines:
            Minpos = min(Minpos, max(0, find_first(line)))

        lines = [line[Minpos:] for line in lines]
        return lines
    
    def parse_raw(lines:list)->str:
        '''
        Don't render these lines.
        '''
        return '<br>'.join(lines)

    def parse_list(lines: list, ListType: str, RE1: str, RE2: str)->str:
        for i in range(lines.count(r'')):
            lines.remove(r'')

        TagBegin = '<' + ListType + ' class="browser-default">'
        TagEnd = '</' + ListType + '>'

        List = ['    ' for i in lines]
        minpos = 9999999

        # delete the blank
        for idx, line in enumerate(lines):
            pos = find_first(line)
            if re.match(RE1, line) != None and pos < minpos:
                minpos = pos
            List[idx] = line[min(pos, minpos):]

        beginpos = -1
        html = r''
        hasli = False
        for idx, line in enumerate(List):
            if re.match(RE2, line) != None:
                log("match", line)
                if beginpos != -1:
                    html += r'<li>' + \
                        parse_block(
                            List[beginpos: idx]) + r'</li>'
                beginpos = idx
                List[idx] = re.sub(RE2, r'\1', line)
                hasli = True
                log("New beginpos", beginpos)
            elif line[0] != ' ':
                log("don't match", line)
                if beginpos != -1:
                    html += r'<li>' + \
                        parse_block(
                            List[beginpos: idx]) + r'</li>'
                    beginpos = -1
                html += parse_line(line) + '<br>'
        # last li
        if beginpos != -1:
            html += r'<li>' + \
                parse_block(
                    List[beginpos: len(List)]) + r'</li>'

        # 增加标签
        if True or hasli:
            html = TagBegin + html + TagEnd

        return html

    @block(r'^[ ]*```(.*?)$', r'(?=^|[ ]+)```$')
    def parse_codeblock(lines: list)->list:
        '''
        Parse codeblock.

        ```python
        print("Hi.") # code here
        ```
        '''
        log(lines)
        res = re.match(r'^[ ]*```[ ]*(.+?)(?: .*)*$', lines[0])

        language = ' class="%s"' % res.group(1) if res else ''
        code = parse_raw(escape_html(delete_space(lines[1:-1])))
        html = r'<pre class="codeblock"><codeblock' + \
            language + '>' + code + r'</codeblock></pre>'
        return html

    @block(r'^>+ .*$', None)
    def parse_quote(lines: list)->str:
        '''
        Markdown quote block.    

        > 1  
        > 2  
        '''
        new_lines = [re.sub(r'^[ ]+(.*?)$', r'\1', line[1:]) for line in lines]
        html = r'<blockquote>' + parse_block(new_lines) + r'</blockquote>'
        return html

    @block(r'^\|(?:.*?\|)+$', None)
    def parse_table(lines: list)->str:
        '''
        表格块转义
        '''

        Table = [list(line.split('|'))[1:-1] for line in lines]
        col = len(Table[0])
        row = len(lines)

        hasAlign = False
        align = ['' for i in range(col)]

        for r in range(row):
            while len(Table[r]) < col:
                Table[r].append('')

        if row > 1:
            for i in range(col):
                if re.match("^\:\-+$", Table[1][i]) != None:
                    align[i] = ' class="left" '
                    hasAlign = True
                    continue
                if re.match("^\:\-+\:$", Table[1][i]) != None:
                    align[i] = ' class="center" '
                    hasAlign = True
                    continue
                if re.match("^\-+\:$", Table[1][i]) != None:
                    align[i] = ' class="right" '
                    hasAlign = True
                    continue
            if hasAlign == True:
                Table.remove(Table[1])
                row -= 1

        html = r''
        for i in range(row):
            html += r'<tr>'

            for j in range(col):
                html += r'<td' + align[j] + r'>' + \
                    parse_line(Table[i][j]) + r'</td>'

            html += r'</tr>'

        html = r'<table class="responsive-table highlight striped">' + html + r'</table>'
        return html

    @block('^[ ]*[\-\*] .*?$', r'^$')
    def parse_ul(lines: list)->list:
        html = parse_list(
            lines, 'ul', r'^[ ]*[\-\*] (.*?)$', r'^[\-\*] (.*?)$')
        return html

    @block(r'^[ ]*[0-9]+\. .*?$', r'^$')
    def parse_ol(lines: list)->str:
        return parse_list(lines, 'ol', r'^[ ]*[0-9]+\. (.*?)$', r'^[0-9]+\. (.*?)$')

    @block(r'\{\% raw \%\}', r'\{\% endraw \%\}')
    @block(r'^\$+$',r'^\$+$')
    def parse_rawblock(lines: list)->list:
        '''
        Markdown raw block.

        {% raw %}
        raw
        {% endraw %}
        '''
        return parse_raw(lines[1:-1])

    @block(r'\{\% fold .*\%\}', r'\{\% endfold \%\}')
    def parse_fold(lines: list)->str:
        '''
        Fold block.

        {% fold title %}
        fold content
        {% endfold %}
        '''
        res = re.match(r'\{\% fold (.*?) \%\}[ ]*(.*)$', lines[0])
        matchList = res.groups() if res else ['', '']
        text = res.group(1) if matchList[0] != '' else '点击显/隐区域'
        if matchList[1] != '':
            lines.insert(1, matchList[1])

        html = '<div class="fold_parent"><div class="fold_hider"><div class="fold_close hider_title">' + \
            text + '</div></div><div class="fold">\n' + \
            parse_block(lines[1:-1]) + '\n</div></div>'
        return html

    @block(r'\{\% cq \%\}', r'\{\% endcq \%\}')
    @block(r'\{\% blockquote \%\}', r'\{\% endblockquote \%\}')
    def parse_center_quote(lines: list)->str:
        '''
        Center quote block.

        {% cq %}
        Content
        {% endcq %}
        '''
        html = r'<blockquote class="center">' + \
            parse_block(lines[1:-1]) + r'</blockquote>'
        return html

    def parse_block(lines: list)->str:
        '''
        Parse markdown block.
        '''
        log(lines)
        block_type = tuple()
        html = []
        begin_pos = -1

        for line_num, line in enumerate(lines):
            if block_type:
                # in block
                log(line, "in block")
                if block_type[1]:
                    # has end block
                    if re.match(block_type[1], line):
                        # is block end
                        log(line, "is block end")
                        html.append(block_type[2](lines[begin_pos:line_num+1]))
                        block_type = None
                        continue
                else:
                    if not re.match(block_type[0], line):
                        # out of block
                        log(line, "out of block")
                        html.append(block_type[2](lines[begin_pos:line_num]))
                        block_type = None

            if not block_type:
                # not in block
                log(line, "not in block")
                for block_type in block_grammer_list:
                    if re.match(block_type[0], line):
                        # block begin
                        log(line, "block begin")
                        begin_pos = line_num
                        break
                else:
                    # render this line directly
                    log("render", line, "directly")
                    block_type = None
                    html.append(parse_line(line))

        if block_type:
            # block don't has end
            log(line, "don't has end")
            html.append(block_type[2](lines[begin_pos:]))

        return "<br>".join(html)

    def escape_html(text: str or list):
        def escape(raw_text: str):
            return raw_text.replace('<', '&lt;')

        if type(text) == list:
            text = [escape(item) for item in text]
        elif type(text) == str:
            text = escape(text)
        else:
            text = escape(str(text))
        return text

    def main():
        nonlocal raw, allow_html
        log("allow_html = ", allow_html)
        if allow_html == False:
            raw = escape_html(raw)
        lines = raw.replace('\t', '    ').replace('\r', '').split('\n')
        html = parse_block(lines)
        return html

    log("block_grammer_list =", block_grammer_list)
    return main()


if __name__ == "__main__":
    raw = ''
    with open("./in.md", "r",encoding = "utf-8") as f:
        raw = f.read()

    raw = r'$\int_{0}^{x} \varphi dt = 1$ '
    markdown = render_markdown(raw, allow_html=True, debug=True)
    print(markdown)
    with open("./out.html", "w",encoding="utf-8")as f:
        f.write(markdown)

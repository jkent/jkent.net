from html import escape
from io import BytesIO
from markdown import markdownFromFile

def convert_to_html(file, mimetype):
    out = BytesIO()

    if mimetype == 'text/html' and data.find(b'<title>') != -1:
        out.write(b'<div class="rendered html">\n')
        while True:
            buf = file.read(16384)
            if not buf:
                break
            out.write(buf)
    elif mimetype == 'text/markdown':
        out.write(b'<div class="rendered markdown">\n')
        markdownFromFile(input=file, output=out, encoding='utf8', extensions=[
            'jkent_net.markdown.codehilite:CodeHiliteExtension',
            'jkent_net.markdown.fenced_code:FencedCodeExtension',
            'tables'
        ])
    elif mimetype == 'text/plain':
        out.write(b'<div class="rendered text">\n')
        while True:
            buf = file.read(16384)
            if not buf:
                break
            out.write(escape(buf))
    else:
        out.write(b'<div class="rendered other">\n')
        while True:
            buf = file.read(16384)
            if not buf:
                break
            out.write(escape(buf))

    out.write(b'\n</div>')
    out.seek(0)
    return out
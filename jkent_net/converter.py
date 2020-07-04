from io import BytesIO
from markdown import markdownFromFile

def escape(s):
    s = s.replace(b'&', b'&amp;')
    s = s.replace(b'<', b'&lt;')
    s = s.replace(b'>', b'&gt;')
    return s

def convert_to_html(file, mimetype):
    out = BytesIO()

    if mimetype == 'text/html':
        buf = file.read(16384)
        if b'<title>' in buf:
            file.seek(0)
            return file, False

        out.write(b'<div class="rendered html">\n')
        while True:
            out.write(buf)
            buf = file.read(16384)
            if not buf:
                break

    elif mimetype == 'text/markdown':
        out.write(b'<div class="rendered markdown">\n')
        markdownFromFile(input=file, output=out, encoding='utf8', extensions=[
            'jkent_net.ext.markdown.codehilite:CodeHiliteExtension',
            'jkent_net.ext.markdown.fenced_code:FencedCodeExtension',
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
    return out, True
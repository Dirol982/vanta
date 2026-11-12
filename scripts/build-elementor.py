"""Turn kitchen-renovation/ into Elementor data for vantasurfaces.com.

Output: elementor/kitchen-dark.json and elementor/kitchen-light.json, each a list of
Elementor elements: one full-width container with class "vk" (plus "vk--light") holding
  - a "styles & script" HTML widget (fonts, scoped CSS, JS),
  - one HTML widget per landing section (editable in Elementor),
  - the site's own vanta_estimate_form widget (Fluent Form #1) in place of the static form.
Images point to the existing WordPress media library files.

Usage: python3 scripts/build-elementor.py
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'kitchen-renovation'
OUT = ROOT / 'elementor'
UP = 'https://vantasurfaces.com/wp-content/uploads/'

# local image -> WordPress media (srcset entries: url width)
IMG = {
    'bayridge-island': [('2026/08/photo_2026-08-22_18-46-36-768x576.jpg', 768), ('2026/08/photo_2026-08-22_18-46-36-1067x800.jpg', 1067), ('2026/08/photo_2026-08-22_18-46-36.jpg', 1280)],
    'gotham-after': [('2026/04/Gotham-After-a1-768x1024.jpg', 768), ('2026/04/Gotham-After-a1-1152x1536.jpg', 1152)],
    'remodel-after': [('2026/10/IMG_2607-768x1029.webp', 768), ('2026/10/IMG_2607-1147x1536.webp', 1147), ('2026/10/IMG_2607.webp', 1792)],
    'remodel-before': [('2026/10/Kitchen-768x1024.webp', 768), ('2026/10/Kitchen.webp', 1086)],
    'stage-rough-in': [('2026/10/kitchen-renovation-timeline-nyc-rough-in-768x432.jpg', 768), ('2026/10/kitchen-renovation-timeline-nyc-rough-in-1300x731.jpg', 1300), ('2026/10/kitchen-renovation-timeline-nyc-rough-in-1536x864.jpg', 1536)],
}


def wp_images(html):
    """Rewrite img/<name>-<w>.webp references (src and srcset) to media-library URLs."""
    def srcset(m):
        names = re.findall(r'img/([a-z-]+)-\d+\.webp', m.group(1))
        name = names[0]
        return 'srcset="' + ', '.join(f'{UP}{u} {w}w' for u, w in IMG[name]) + '"'
    html = re.sub(r'srcset="([^"]*)"', srcset, html)

    def src(m):
        name = m.group(1)
        files = IMG[name]
        pick = files[-1] if m.group(2) == '1600' else files[0]
        return f'src="{UP}{pick[0]}"'
    html = re.sub(r'src="(?:\.\./)?img/([a-z-]+)-(\d+)\.webp"', src, html)
    assert 'img/' not in re.sub(r'wp-content/uploads', '', html).replace(UP, ''), 'unmapped image left'
    return html


def scope_css(css):
    """Prefix every selector with .vk so the landing styles cannot leak into or be hit by the theme."""
    out = []
    i = 0
    n = len(css)

    def scope_sel(sel):
        parts = []
        for s in sel.split(','):
            s = s.strip()
            if not s:
                continue
            if s.startswith(':root[data-theme=\'light\']'):
                s = '.vk.vk--light' + s[len(":root[data-theme='light']"):]
            elif s == ':root':
                s = '.vk'
            elif s in ('html', 'body'):
                s = '.vk'
            elif s.startswith('.m '):
                s = '.vk.m ' + s[3:]
            elif s.startswith('*'):
                s = '.vk ' + s
            else:
                s = '.vk ' + s
            parts.append(s)
        return ', '.join(parts)

    def block(start):
        depth, j = 0, start
        while j < n:
            if css[j] == '{':
                depth += 1
            elif css[j] == '}':
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        raise ValueError('unbalanced css')

    while i < n:
        if css.startswith('/*', i):
            j = css.index('*/', i) + 2
            i = j
            continue
        if css[i].isspace():
            i += 1
            continue
        k = css.index('{', i)
        head = css[i:k].strip()
        end = block(k)
        body = css[k + 1:end]
        if head.startswith('@keyframes'):
            out.append(head + '{' + body + '}')
        elif head.startswith('@media') or head.startswith('@supports'):
            out.append(head + '{' + scope_css(body) + '}')
        elif head == 'html':
            pass  # page-level; Elementor page keeps the theme's html rules
        else:
            out.append(scope_sel(head) + '{' + body.strip() + '}')
        i = end + 1
    return '\n'.join(out)


EXTRA_CSS = """
/* Elementor / theme resets inside the landing */
.vk { font: 400 1rem/1.55 var(--f-text); background: var(--bg); color: var(--fg); overflow-x: clip; }
.vk .elementor-widget:not(:last-child) { margin-block-end: 0; }
.vk .elementor-widget-container { margin: 0; padding: 0; }
.vk h1, .vk h2, .vk h3 { color: inherit; }
.vk .h2, .vk .mega, .vk .book__title, .vk .path__name { color: var(--fg); }
.vk button { text-transform: none; letter-spacing: normal; box-shadow: none; line-height: 1; }
.vk ul, .vk ol { margin: 0; }
@media (max-width: 640px) { .vk .top .btn { margin-left: auto !important; } }
.vk a:not(.btn):hover { color: inherit; }
/* the site's estimate form widget inside the landing */
.vk .vanta-estimate-form { background: transparent !important; padding: 0 var(--m) clamp(40px, 5vw, 72px) !important; margin: 0 !important; }
.vk .vanta-estimate-form__inner { max-width: none !important; padding: 0 !important; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: var(--gap); align-items: start; }
.vk .vanta-estimate-form__header { text-align: left !important; margin: 0 !important; padding-top: 8px; }
.vk .vanta-estimate-form__title { font: 700 clamp(1.3rem, 2vw, 1.8rem)/1.15 var(--f-display) !important; text-transform: uppercase; letter-spacing: -.02em !important; color: var(--fg) !important; margin: 0 0 12px !important; }
.vk .vanta-estimate-form__description { color: var(--muted) !important; font: 400 1rem/1.55 var(--f-text) !important; }
.vk .vanta-estimate-form__form-shell { margin: 0 !important; max-width: none !important; border-radius: var(--r) !important; }
@media (max-width: 860px) { .vk .vanta-estimate-form__inner { grid-template-columns: 1fr; } }
"""


def build_js(js):
    js = js.replace("var root = document.documentElement;", "var root = document.querySelector('.vk');\n  if (!root) return;")
    js = js.replace("document.body.prepend(bar);", "root.prepend(bar);")
    js = js.replace("var max = root.scrollHeight - innerHeight;", "var max = document.documentElement.scrollHeight - innerHeight;")
    # the static form is replaced by the site's Fluent Form: drop the form handler and point the CTA observer at the widget
    s = js.index('  /* ── Form ── */')
    e = js.index('  /* ── Mobile sticky call-to-action ── */')
    js = js[:s] + js[e:]
    js = js.replace("book = document.getElementById('book');", "book = document.getElementById('vanta-estimate-form') || document.getElementById('book');")
    js = js.replace("  var ENDPOINT = window.VANTA_FORM_ENDPOINT || '';\n", '')
    return js


def rid():
    return '%07x' % random.getrandbits(28)


def html_widget(title, html):
    return {'id': rid(), 'elType': 'widget', 'widgetType': 'html', 'elements': [],
            'settings': {'html': html.strip(), '_title': title}}


def sections(page):
    body = page[page.index('<body>') + 6:page.index('</body>')]
    body = body.replace('<a class="theme-link" href="light/">Light version</a>\n', '')
    body = re.sub(r'<a class="skip"[^>]*>.*?</a>\s*', '', body)
    body = re.sub(r'<script src="app\.js" defer></script>\s*', '', body)
    body = body.replace('<main id="main">', '').replace('</main>', '')
    parts = []
    header = re.search(r'<header class="top">.*?</header>', body, re.S).group(0)
    parts.append(('Header', header))
    for name, pat in [
        ('Hero', r'<section class="hero".*?</section>'),
        ('Ticker', r'<div class="ticker".*?</div></div>'),
        ('01 Paths', r'<section class="sec" id="paths">.*?</section>'),
        ('02 Process', r'<section class="sec" id="process">.*?</section>'),
        ('03 Before & after', r'<section class="sec sec--panel" id="work">.*?</section>'),
        ('04 Reviews', r'<section class="sec" id="reviews">.*?</section>'),
        ('05 FAQ', r'<section class="sec sec--panel" id="faq">.*?</section>'),
    ]:
        parts.append((name, re.search(pat, body, re.S).group(0)))
    book = re.search(r'<section class="book" id="book">.*?</section>', body, re.S).group(0)
    head = re.search(r'<div class="book__head">.*?</div>', book, re.S).group(0)
    call = re.search(r'<div class="book__call">.*?</div>', book, re.S).group(0)
    parts.append(('Estimate title', f'<section class="book book--head" id="book">\n  {head}\n</section>'))
    parts.append(('FORM', None))
    parts.append(('Call line', f'<div class="book book--call">\n  {call}\n</div>'))
    foot = re.search(r'<footer class="foot">.*?</footer>', body, re.S).group(0)
    mcta = re.search(r'<div class="mobile-cta">.*?</div>', body, re.S).group(0)
    parts.append(('Footer', foot + '\n' + mcta))
    return parts


def main():
    page = (SRC / 'index.html').read_text()
    css = scope_css((SRC / 'styles.css').read_text()) + EXTRA_CSS
    css += '\n.vk .book--head { padding-bottom: 28px; }\n.vk .book--call { padding-top: 0; }\n'
    js = build_js((SRC / 'app.js').read_text())
    ld = re.search(r'<script type="application/ld\+json">.*?</script>', page, re.S).group(0)
    fonts = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]+>', page).group(0)
    assets = (f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n{fonts}\n'
              f'<style id="vk-css">\n{css}\n</style>\n{ld}\n'
              f'<script data-no-optimize="1">\ndocument.addEventListener("DOMContentLoaded", function () {{\n{js}\n}});\n</script>')
    OUT.mkdir(exist_ok=True)
    for theme in ('dark', 'light'):
        random.seed(theme)
        widgets = [html_widget('Styles & script (do not delete)', assets)]
        for name, html in sections(page):
            if html is None:
                widgets.append({'id': rid(), 'elType': 'widget', 'widgetType': 'vanta_estimate_form', 'elements': [],
                                'settings': {'heading': 'Tell us what you need done',
                                             'description': 'Fill in the form and our team will contact you shortly.'}})
            else:
                widgets.append(html_widget(name, wp_images(html)))
        container = {
            'id': rid(), 'elType': 'container', 'isInner': False, 'elements': widgets,
            'settings': {
                'content_width': 'full', 'css_classes': 'vk' + (' vk--light' if theme == 'light' else ''),
                'flex_direction': 'column', 'flex_gap': {'unit': 'px', 'size': 0, 'column': '0', 'row': '0'},
                'padding': {'unit': 'px', 'top': '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': True},
                'margin': {'unit': 'px', 'top': '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': True},
            },
        }
        (OUT / f'kitchen-{theme}.json').write_text(json.dumps([container], ensure_ascii=False, indent=1))
        print('wrote', OUT / f'kitchen-{theme}.json', len(widgets), 'widgets')


if __name__ == '__main__':
    main()

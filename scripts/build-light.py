"""Build kitchen-renovation/light/index.html (light theme) from kitchen-renovation/index.html.
Run after editing the dark page:  python3 scripts/build-light.py"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent / 'kitchen-renovation'
h = (root / 'index.html').read_text()
swaps = [
    ('<html lang="en">', '<html lang="en" data-theme="light">'),
    ('<meta name="theme-color" content="#11131b">', '<meta name="theme-color" content="#f7f5f1">'),
    ('href="styles.css"', 'href="../styles.css"'),
    ('src="app.js"', 'src="../app.js"'),
    ('"img/', '"../img/'),
    (' img/', ' ../img/'),
    ('<a class="theme-link" href="light/">Light version</a>', '<a class="theme-link" href="../">Dark version</a>'),
]
for a, b in swaps:
    if a not in h:
        raise SystemExit(f'pattern not found: {a}')
    h = h.replace(a, b)
out = root / 'light' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(h)
print('wrote', out)

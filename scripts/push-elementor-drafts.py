"""Create (or update) DRAFT pages and Elementor library templates on vantasurfaces.com
from elementor/kitchen-{dark,light}.json. Never publishes: every post is saved with status "draft".

Auth comes from the environment's network proxy (WordPress application password); no secret is read here.
State (created post IDs) is kept in elementor/wp-ids.json so a re-run updates the same drafts.
"""
import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://vantasurfaces.com/wp-json/wp/v2/'
CA = '/root/.ccr/ca-bundle.crt'
ctx = ssl.create_default_context(cafile=CA) if Path(CA).exists() else ssl.create_default_context()
STATE = ROOT / 'elementor' / 'wp-ids.json'


def req(path, data=None):
    body = json.dumps(data, ensure_ascii=False).encode() if data is not None else None
    r = urllib.request.Request(API + path, data=body, method='POST' if body else 'GET',
                               headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'vanta-admin'})
    try:
        return json.load(urllib.request.urlopen(r, context=ctx, timeout=90))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{e.code} {path}: {e.read().decode()[:400]}')


def main():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for theme in ('dark', 'light'):
        data = (ROOT / 'elementor' / f'kitchen-{theme}.json').read_text()
        label = 'Dark' if theme == 'dark' else 'Light'
        meta = {'_elementor_edit_mode': 'builder', '_elementor_data': data}
        jobs = [
            ('pages', f'page-{theme}', {
                'title': f'Kitchen Renovation NYC — Landing ({label})',
                'slug': f'kitchen-renovation-nyc{"" if theme == "dark" else "-light"}',
                'status': 'draft', 'template': 'elementor_canvas',
                'meta': {**meta, '_elementor_template_type': 'wp-page'},
            }),
            ('elementor_library', f'tpl-{theme}', {
                'title': f'Landing — Kitchen Renovation ({label})',
                'status': 'draft',
                'meta': {**meta, '_elementor_template_type': 'page'},
            }),
        ]
        for route, key, payload in jobs:
            path = f'{route}/{state[key]}' if key in state else route
            r = req(path + '?_fields=id,status,link,type', payload)
            if r.get('status') != 'draft':
                raise SystemExit(f'{key} is {r.get("status")}, expected draft')
            state[key] = r['id']
            print(key, r['id'], r['status'], r.get('link'))
    STATE.write_text(json.dumps(state, indent=1))


if __name__ == '__main__':
    main()

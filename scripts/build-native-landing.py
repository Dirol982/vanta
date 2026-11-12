"""Kitchen landing built only from the site's own Elementor widgets (vanta-elementor-blocks), so it matches
the vantasurfaces.com design. Starts from the live /kitchen-remodeling/ page data and saves a DRAFT page.

Usage: python3 scripts/build-native-landing.py
"""
import copy
import html
import json
import random
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://vantasurfaces.com/wp-json/'
CA = '/root/.ccr/ca-bundle.crt'
ctx = ssl.create_default_context(cafile=CA) if Path(CA).exists() else ssl.create_default_context()
STATE = ROOT / 'elementor' / 'wp-ids.json'
KITCHEN_PAGE = 31481


def req(path, data=None):
    body = json.dumps(data, ensure_ascii=False).encode() if data is not None else None
    r = urllib.request.Request(API + path, data=body, method='POST' if body else 'GET',
                               headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'vanta-admin'})
    try:
        return json.load(urllib.request.urlopen(r, context=ctx, timeout=90))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{e.code} {path}: {e.read().decode()[:400]}')


def rid():
    return '%07x' % random.getrandbits(28)


def reid(node):
    node['id'] = rid()
    for v in node.get('settings', {}).values():
        if isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and '_id' in it:
                    it['_id'] = rid()
    for ch in node.get('elements', []):
        reid(ch)
    return node


def find(el, wtype):
    for c in el:
        for w in c['elements']:
            if w.get('widgetType') == wtype:
                return copy.deepcopy(w)
    raise SystemExit('widget not found: ' + wtype)


def container(*widgets):
    return {'id': rid(), 'elType': 'container', 'isInner': False, 'settings': {'scroll_y': -80}, 'elements': list(widgets)}


def main():
    random.seed('native-landing')
    src = req(f'wp/v2/pages/{KITCHEN_PAGE}?context=edit&_fields=template,meta')
    el = json.loads(src['meta']['_elementor_data'])

    # 1. Hero
    hero = find(el, 'vanta_service_hero')
    hero['settings'].update({
        'eyebrow': 'REFRESH · REFACE · REPLACE',
        'heading': 'Kitchen Renovation in NYC',
        'description': 'Refresh, reface or fully replace your kitchen. Licensed and insured, co-op and condo ready.',
        'primary_cta_text': 'Get a Free Estimate',
        'primary_cta_link': {'url': '#vanta-estimate-form', 'is_external': '', 'nofollow': '', 'custom_attributes': ''},
        'secondary_cta_text': 'Compare the Options',
        'secondary_cta_link': {'url': '#kitchen-options', 'is_external': '', 'nofollow': '', 'custom_attributes': ''},
        'background_image': {'url': 'https://vantasurfaces.com/wp-content/uploads/2026/08/photo_2026-08-22_18-46-36.jpg',
                             'id': 30579, 'size': '', 'alt': 'Blue kitchen island refinished in interior film, Bay Ridge, Brooklyn', 'source': 'library'},
    })

    # 2. Three paths, on the site's own "inclusions" card block
    paths = find(el, 'vanta_service_inclusions')
    paths['settings'].update({
        'eyebrow': 'THREE WAYS TO UPDATE YOUR KITCHEN',
        'heading': "Most kitchens don't need a tear-out",
        'intro_text': 'Pick the option closest to your plan. Your written estimate confirms the scope and dates for your kitchen and building.',
        'cards': [
            {'title': 'Refresh', 'is_highlighted': 'yes',
             'description': 'New finish on existing cabinet doors, boxes and island in architectural film. Our Bay Ridge kitchen took 3 days on site with 0 days out of use.',
             'icon': {'value': 'fas fa-paint-roller', 'library': 'fa-solid'}},
            {'title': 'Reface',
             'description': 'New doors, drawer fronts and hardware on your existing boxes, with optional countertop, backsplash and lighting. Layout and plumbing stay.',
             'icon': {'value': 'fas fa-door-open', 'library': 'fa-solid'}},
            {'title': 'Replace',
             'description': 'Full remodel: layout, cabinets, countertops, plumbing, electrical, flooring and lighting, with board paperwork and permits handled by us.',
             'icon': {'value': 'fas fa-hammer', 'library': 'fa-solid'}},
        ],
        'strip_text': 'Not sure which one fits? We walk the kitchen with you and recommend the option that fits your budget.',
        'cta_text': 'GET A FREE ESTIMATE',
    })
    paths['settings']['_element_id'] = 'kitchen-options'

    # 3. Process (dark block)
    details = find(el, 'vanta_service_details')
    details['settings'].update({
        'eyebrow': 'KITCHEN RENOVATION IN NYC',
        'heading': 'Every detail handled.\nOne team from\nstart to finish.',
        'description': 'We measure and agree the scope, prepare the co-op or condo paperwork, COI and elevator bookings, order materials before demolition and keep one project manager on your job until handover.',
    })

    # 4. Proof
    reviews = find(el, 'vanta_google_reviews_shortcode')
    compare = find(el, 'vanta_before_rendering_after')

    # 5. Form and FAQ
    form = find(el, 'vanta_estimate_form')
    faq = find(el, 'vanta_faq')
    items = faq['settings']['items']
    items.insert(1, {'question': 'Do I need board approval in a co-op or condo?',
                     'answer': '<p>For most work beyond a refresh, yes. We prepare the alteration paperwork, certificates of insurance and work schedule your building asks for, and coordinate with the managing agent.</p>'})
    faq['settings']['heading'] = 'Kitchen renovation questions'
    txt = lambda h: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': txt(i['question']), 'acceptedAnswer': {'@type': 'Answer', 'text': txt(i['answer'])}} for i in items]}
    schema = {'elType': 'widget', 'widgetType': 'html', 'elements': [],
              'settings': {'html': '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', '_title': 'FAQ schema'}}

    motion = {'elType': 'widget', 'widgetType': 'html', 'elements': [],
              'settings': {'html': (ROOT / 'elementor' / 'motion-layer.html').read_text(), '_title': 'Motion layer (parallax & animations)'}}
    data = [container(hero), container(paths), container(details), container(reviews, compare),
            container(form), container(faq, schema, motion)]
    for c in data:
        reid(c)
    out = ROOT / 'elementor' / 'kitchen-native.json'
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))

    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    payload = {'title': 'Kitchen Renovation NYC — Landing (site design)', 'slug': 'kitchen-renovation-nyc-landing',
               'status': 'draft', 'template': src['template'],
               'meta': {'_elementor_edit_mode': 'builder', '_elementor_template_type': 'wp-page',
                        '_elementor_data': json.dumps(data, ensure_ascii=False)}}
    path = f"wp/v2/pages/{state['page-native']}" if 'page-native' in state else 'wp/v2/pages'
    r = req(path + '?_fields=id,status,link', payload)
    if r['status'] != 'draft':
        raise SystemExit('expected draft, got ' + r['status'])
    state['page-native'] = r['id']
    STATE.write_text(json.dumps(state, indent=1))
    # landing for paid traffic duplicates /kitchen-remodeling/: keep it out of search
    req('rankmath/v1/updateMeta', {'objectType': 'post', 'objectID': r['id'], 'meta': {
        'rank_math_robots': ['noindex', 'follow'],
        'rank_math_title': 'Kitchen Renovation in NYC | Vanta Surfaces',
        'rank_math_description': 'Refresh, reface or fully replace your kitchen. Licensed and insured NYC contractor, co-op and condo ready. Free walkthrough and written estimate.'}})
    print('draft', r['id'], r['link'], 'template', src['template'])


if __name__ == '__main__':
    main()

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
        'background_image': {'url': 'https://vantasurfaces.com/wp-content/uploads/2026/10/photo_2026-10-07_02-44-43.jpg',
                             'id': 31663, 'size': '', 'alt': 'Renovated kitchen with wood and white cabinets and an island', 'source': 'library'},
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
        'strip_text': 'Not sure which option fits? We walk the kitchen with you, check what can stay and recommend the right option for your budget.',
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
    def htmlw(title, code):
        return {'elType': 'widget', 'widgetType': 'html', 'elements': [], 'settings': {'html': code, '_title': title}}

    def row(css, *widgets, bg=None):
        c = container(*widgets)
        c['settings'].update({'content_width': 'full', 'css_classes': css})
        if bg:
            c['settings'].update({'background_background': 'classic', 'background_color': bg})
        return c

    layout = htmlw('Landing layout styles (keep)', (ROOT / 'elementor' / 'landing-layout.html').read_text())
    next_panel = htmlw('What happens next', '''<div class="vk-next">
  <p class="vk-eyebrow">Free estimate</p>
  <h2>What happens after you send the form</h2>
  <ol class="vk-steps">
    <li><span>01</span><div><strong>We call you back</strong><p>We review your request and call to schedule a walkthrough at a time that works for you.</p></div></li>
    <li><span>02</span><div><strong>Walkthrough and measurements</strong><p>We measure the kitchen, check what your building requires and talk through the options.</p></div></li>
    <li><span>03</span><div><strong>Written estimate</strong><p>You get an itemized scope and price in writing, free of charge.</p></div></li>
  </ol>
  <div class="vk-next__contact">
    <span>Prefer to talk?</span>
    <a href="tel:+16466641696">(646) 664-1696</a>
    <span><span class="vk-next__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span> 4.9 on Google · Licensed &amp; insured · NYC DCWP 2137851</span>
  </div>
</div>''')
    faq_side = htmlw('FAQ heading', '''<div class="vk-faq-side">
  <p class="vk-eyebrow">FAQ</p>
  <h2>Questions owners ask before they book</h2>
  <p>Don't see yours? Call <a class="vk-link" href="tel:+16466641696">(646) 664-1696</a> or add it to your estimate request.</p>
  <div><a class="vk-btn" href="#vanta-estimate-form">Get a free estimate</a></div>
</div>''')
    data = [container(layout, hero), container(paths), container(details), container(reviews, compare),
            row('vk-split', next_panel, form, bg='#ffffff'), row('vk-faq', faq_side, faq, schema, motion, bg='#f7f5f1')]
    for c in data:
        reid(c)
    out = ROOT / 'elementor' / 'kitchen-native.json'
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))

    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    payload = {'title': 'Kitchen Renovation NYC — Landing (site design)', 'template': src['template'],
               'meta': {'_elementor_edit_mode': 'builder', '_elementor_template_type': 'wp-page',
                        '_elementor_data': json.dumps(data, ensure_ascii=False)}}
    if 'page-native' in state:  # update content only: status and slug stay as they are on the site
        r = req(f"wp/v2/pages/{state['page-native']}?_fields=id,status,link", payload)
    else:
        payload.update({'status': 'draft', 'slug': 'kitchen-renovation-nyc-landing'})
        r = req('wp/v2/pages?_fields=id,status,link', payload)
    state['page-native'] = r['id']
    STATE.write_text(json.dumps(state, indent=1))
    # landing for paid traffic duplicates /kitchen-remodeling/: keep it out of search
    req('rankmath/v1/updateMeta', {'objectType': 'post', 'objectID': r['id'], 'meta': {
        'rank_math_robots': ['noindex', 'follow'],
        'rank_math_title': 'Kitchen Renovation in NYC | Vanta Surfaces',
        'rank_math_description': 'Refresh, reface or fully replace your kitchen. Licensed and insured NYC contractor, co-op and condo ready. Free walkthrough and written estimate.'}})
    print(r['status'], r['id'], r['link'], 'template', src['template'])


if __name__ == '__main__':
    main()

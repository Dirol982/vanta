# vanta

Landing pages for [Vanta Surfaces](https://vantasurfaces.com), served with GitHub Pages.

| Page | Folder |
|---|---|
| Kitchen renovation in NYC (dark) | `kitchen-renovation/` |
| Kitchen renovation in NYC (light) | `kitchen-renovation/light/` |

Each landing is static HTML, CSS and JS with no build step. The light page is generated from the dark one:
after editing `kitchen-renovation/index.html`, run `python3 scripts/build-light.py`. Photos are the company's own project photos, resized to WebP.

## Lead form

Without configuration the estimate form opens a pre-filled email to the office. To send leads to a backend instead,
define the endpoint before `app.js` loads:

```html
<script>window.VANTA_FORM_ENDPOINT = "https://example.com/webhook";</script>
```

The form then POSTs JSON: `name, phone, email, zip, option, message, page`.

## Elementor version on vantasurfaces.com

`python3 scripts/build-elementor.py` turns `kitchen-renovation/` into Elementor data (`elementor/kitchen-{dark,light}.json`):
one full-width container with class `vk` (`vk vk--light` for the light theme), a "Styles & script" HTML widget,
one HTML widget per section, and the site's own `vanta_estimate_form` widget (Fluent Form #1) as the lead form.
Styles are scoped to `.vk` so the theme cannot override them. Images use the WordPress media library.

`python3 scripts/push-elementor-drafts.py` saves them to the site as **drafts** (pages with the Elementor Canvas
template plus Elementor library templates). IDs are kept in `elementor/wp-ids.json`, so re-running updates the same drafts.

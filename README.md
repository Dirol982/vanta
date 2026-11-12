# vanta

Landing pages for [Vanta Surfaces](https://vantasurfaces.com), served with GitHub Pages.

| Page | Folder |
|---|---|
| Kitchen renovation in NYC | `kitchen-renovation/` |

Each landing is static HTML, CSS and JS with no build step. Photos are the company's own project photos, resized to WebP.

## Lead form

Without configuration the estimate form opens a pre-filled email to the office. To send leads to a backend instead,
define the endpoint before `app.js` loads:

```html
<script>window.VANTA_FORM_ENDPOINT = "https://example.com/webhook";</script>
```

The form then POSTs JSON: `name, phone, email, zip, option, message, page`.

# careerhubnagaland.in

Static site for Career Hub Nagaland, built with `build.py` (Python 3, no dependencies).

- `src/pages/*.html` page bodies; the first line holds page metadata (title, description, FAQ).
- `src/assets/` styles and the small form script.
- `src/static/` server files: `.htaccess` (redirects, headers) and `enquire.php` (enquiry handler).
- Site facts (phone, email, address, GA4 ID) are set once at the top of `build.py`.

Build: `python3 build.py --staging` (noindex) or `python3 build.py` (production). Output goes to `dist/`.

Deploy branches: `staging` and `production` each hold a built `dist/` at the repository root; Hostinger pulls them into `public_html`.

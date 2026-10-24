#!/usr/bin/env python3
"""Build the Career Hub Nagaland static site.

Usage: python3 build.py [--staging]
Pages live in src/pages/*.html. The first line of each page is
<!--META {json}--> holding path, title, description, nav, cta and faq.
Placeholders in page bodies: {{WA:message|source}}, {{PHONE}}, {{TEL}},
{{EMAIL}}, {{ADDRESS}}, {{FAQ}}.
"""
import hashlib, html, json, os, re, shutil, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "dist"
STAGING = "--staging" in sys.argv

# ---- Site facts: change once here, used everywhere ----
SITE = "https://careerhubnagaland.in"
NAME = "Career Hub Nagaland"
PHONE = "+91 93660 92897"
TEL = "+919366092897"
WA_NUMBER = "919366092897"
EMAIL = "emmanuelyanthan@rediffmail.com"   # replace with hello@careerhubnagaland.in once the mailbox exists
ADDRESS = "Evita Building, Burma Camp, Dimapur, Nagaland"
GA4_ID = ""                                 # e.g. G-XXXXXXX; leave empty until the property exists
UPDATED = "24 October 2026"

# Razorpay Payment Pages (rzp.io short links). Leave a value empty to fall back to the enquiry form.
PAY = {
    "assessment": "https://rzp.io/rzp/deibG8e",
    "counselling": "https://rzp.io/rzp/Quu4cOnr",
    "group": "https://rzp.io/rzp/tTCuKIJ",
    "clarity": "https://rzp.io/rzp/4FDijUy3",
    "readiness": "https://rzp.io/rzp/dLOta7c",
    "readiness-balance": "https://rzp.io/rzp/ffnprXR",
}

NAV = [
    ("home", "/", "Grades 8–12"),
    ("graduates", "/college-and-graduates-job-readiness/", "Graduates"),
    ("schools", "/for-schools/", "For schools"),
    ("fees", "/fees/", "Fees"),
    ("about", "/about/", "About"),
    ("contact", "/contact/", "Contact"),
]


def wa(message, source):
    text = f"{message} ({source})"
    return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(text)}"


def org_graph():
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "ProfessionalService",
                "@id": f"{SITE}/#org",
                "name": NAME,
                "description": "Career counselling practice in Dimapur, Nagaland, for students in Grades 8–12 and graduates. An initiative of ICATAN.",
                "url": f"{SITE}/",
                "logo": f"{SITE}/assets/img/icon-512.png",
                "image": f"{SITE}/assets/img/share.jpg",
                "telephone": PHONE,
                "email": EMAIL,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Evita Building, Burma Camp",
                    "addressLocality": "Dimapur",
                    "addressRegion": "Nagaland",
                    "addressCountry": "IN",
                },
                "areaServed": ["Dimapur", "Nagaland"],
                "parentOrganization": {"@type": "Organization", "name": "ICATAN"},
                "founder": {"@id": f"{SITE}/about/#person"},
            },
            {
                "@type": "Person",
                "@id": f"{SITE}/about/#person",
                "name": "Dr. Emmanuel L. Yanthan",
                "jobTitle": "Lead Career Counsellor",
                "image": f"{SITE}/assets/img/counsellor-640.jpg",
                "worksFor": {"@id": f"{SITE}/#org"},
                "hasCredential": {
                    "@type": "EducationalOccupationalCredential",
                    "name": "Global Career Counsellor (Univariety and UCLA Extension)",
                },
            },
        ],
    }


def faq_html(items):
    out = ['<div class="faq">']
    for q, a in items:
        out.append(f"<details><summary>{html.escape(q)}</summary><div><p>{a}</p></div></details>")
    out.append("</div>")
    return "\n".join(out)


def faq_ld(items):
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in items
        ],
    }


def render_header(active):
    links = []
    for key, href, label in NAV:
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    links_html = "".join(links)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/img/logo-horizontal.webp" width="781" height="200" alt="Career Hub Nagaland, home"></a>
    <nav class="nav" aria-label="Main">{links_html}<a class="btn btn-primary" href="/enquire/">Book a free call</a></nav>
    <details class="menu"><summary>Menu</summary><nav aria-label="Main">{links_html}<a href="/enquire/">Book a free call</a></nav></details>
  </div>
</header>"""


def render_footer(cta_src):
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>Career Hub Nagaland</h2>
        <p>A career counselling practice in Dimapur for students in Grades 8–12 and graduates. An initiative of ICATAN.</p>
      </div>
      <div>
        <h2>Visit or call</h2>
        <ul>
          <li>{ADDRESS}</li>
          <li><a href="tel:{TEL}">{PHONE}</a></li>
          <li><a href="{wa('Hello Career Hub Nagaland, I have a question.', 'web-footer')}">Message on WhatsApp</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
      <div>
        <h2>Pages</h2>
        <ul>
          <li><a href="/fees/">Fees and booking</a></li>
          <li><a href="/for-schools/">For schools</a></li>
          <li><a href="/safeguarding/">Safeguarding and consent</a></li>
          <li><a href="/privacy/">Privacy notice</a></li>
          <li><a href="/terms/">Terms and refunds</a></li>
        </ul>
      </div>
    </div>
    <p class="legal">© 2026 Career Hub Nagaland, an initiative of ICATAN. We do not guarantee admissions, results or jobs; we help families decide with better information.</p>
  </div>
</footer>
<div class="action-bar">
  <a class="btn btn-primary" href="/enquire/">Book a free call</a>
  <a class="btn btn-secondary" href="{wa('Hello Career Hub Nagaland, I would like to know more.', cta_src)}">WhatsApp</a>
</div>"""


def asset_version(name):
    return hashlib.sha1((SRC / "assets" / name).read_bytes()).hexdigest()[:8]


def render_page(meta, body):
    path = meta["path"]
    canonical = SITE + path
    title = meta["title"]
    desc = meta["description"]
    ld = [org_graph()]
    if meta.get("faq"):
        ld.append(faq_ld(meta["faq"]))
    for extra in meta.get("jsonld", []):
        ld.append(extra)
    ld_html = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld
    )
    robots = '<meta name="robots" content="noindex, nofollow">' if (STAGING or meta.get("noindex")) else ""
    ga = ""
    if GA4_ID and not STAGING:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
              f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>")

    def sub(m):
        msg, src = m.group(1).split("|")
        return html.escape(wa(msg, src))

    body = re.sub(r"\{\{WA:([^}]+)\}\}", sub, body)
    body = re.sub(r"\{\{PAY:([a-z-]+)\}\}", lambda m: PAY.get(m.group(1)) or f"/enquire/?service={m.group(1)}", body)
    body = (body.replace("{{PHONE}}", PHONE).replace("{{TEL}}", TEL)
                .replace("{{EMAIL}}", EMAIL).replace("{{ADDRESS}}", ADDRESS)
                .replace("{{UPDATED}}", UPDATED))
    if meta.get("faq"):
        body = body.replace("{{FAQ}}", faq_html(meta["faq"]))

    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/img/share.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Career Hub Nagaland logo">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta name="theme-color" content="#3a2d28">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Literata:opsz,wght@7..72,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={asset_version('site.css')}">
{ld_html}
{ga}
</head>
<body>
{render_header(meta.get('nav', ''))}
<main id="main">
{body}
</main>
{render_footer(meta.get('cta', 'web'))}
<script src="/assets/site.js?v={asset_version('site.js')}" defer></script>
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")
    for f in (SRC / "static").iterdir():
        shutil.copy(f, OUT / f.name)
    urls = []
    for page in sorted((SRC / "pages").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        first, body = text.split("\n", 1)
        meta = json.loads(re.match(r"<!--META (.*)-->", first).group(1))
        out = OUT / meta["path"].lstrip("/")
        if meta["path"].endswith("/"):
            out = out / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page(meta, body), encoding="utf-8")
        if not meta.get("noindex") and meta["path"] != "/404.html":
            urls.append(meta["path"])
    # robots and sitemap
    if STAGING:
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    else:
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{SITE}{u}</loc><lastmod>2026-10-24</lastmod></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    # htaccess: staging adds a no-index header
    ht = (SRC / "static" / ".htaccess").read_text()
    if STAGING:
        ht += '\n<IfModule mod_headers.c>\nHeader set X-Robots-Tag "noindex, nofollow"\n</IfModule>\n'
    (OUT / ".htaccess").write_text(ht)
    print(f"Built {len(urls)} indexable pages into {OUT} ({'staging' if STAGING else 'production'})")


if __name__ == "__main__":
    main()

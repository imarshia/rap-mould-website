#!/usr/bin/env python3
"""R.A.P MOULD, single-source static site builder.
Run: python3 src/build.py   -> writes dist/
SEO: unique title/description/canonical/OG per page, JSON-LD, sitemap.xml, robots.txt
"""
import os, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')

SITE = {
    'name': 'R.A.P MOULD',
    'full_name': 'Rahkar Andishan Pars Ghaleb',
    'tagline': 'Precision Mold Design & Manufacturing',
    # TODO: replace with the real domain before launch (canonical + sitemap depend on it)
    'base_url': 'https://rapmould.com',
    'email1': 'adss_2012@yahoo.com',
    'email2': 'dsadralzakerin@gmail.com',
    'phone1': '+98 919 960 5799',
    'phone2': '+98 935 802 5802',
    'phone1_href': '+989199605799',
    'phone2_href': '+989358025802',
    'address': 'Bojnord, North Khorasan, Iran',
    # TODO: replace with your real Cloudflare Turnstile site key
    # (Cloudflare dashboard > Turnstile > Add site). Required for the contact form captcha.
    'turnstile_site_key': '0x4AAAAAAFNSbJRpnmzxKwTG',
}

NAV = [
    ('/', 'Home'),
    ('/about/', 'About Us'),
    ('/services/', 'Services'),
    ('/case-studies/', 'Case Studies'),
    ('/facilities/', 'Facilities'),
    ('/process/', 'Our Process'),
    ('/contact/', 'Contact'),
]

SERVICES = [
    ('plastic-injection-molds', 'Plastic Injection Molds',
     'Design and precision manufacturing of plastic injection molds.',
     'Custom injection molds for automotive, appliance, hygiene, and packaging parts.'),
    ('die-cast-molds', 'Die-Cast Molds',
     'High-pressure die-cast molds built for dimensional stability.',
     'Durable die-casting tooling engineered for repeatable, high-volume output.'),
    ('progressive-press-molds', 'Press & Progressive Molds',
     'Metal press and progressive (staged) molds for sheet-metal parts.',
     'Progressive and single-stage press tooling for efficient sheet-metal forming.'),
    ('cnc-machining', 'CNC Machining',
     'High-accuracy turning and milling for mold components.',
     'Precision CNC turning and milling for mold parts and industrial components.'),
    ('reverse-engineering', 'Reverse Engineering',
     'Rebuilding undocumented parts and molds from physical samples.',
     'From a worn part or sample to production-ready 3D models and tooling.'),
    ('mold-repair-maintenance', 'Mold Repair & Maintenance',
     'Extending mold life with expert repair and preventive care.',
     'Repair, refurbishment, and maintenance programs that keep molds running.'),
]

# ---------------- icons (inline SVG, stroke) ----------------
def _ic(paths, vb='0 0 24 24'):
    return (f'<svg viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')

ICONS = {
    'mold': _ic('<rect x="4" y="7" width="16" height="10" rx="2"/><path d="M4 10h16M9 7V4m6 3V4M9 17v3m6-3v3"/>'),
    'layers': _ic('<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>'),
    'gear': _ic('<circle cx="12" cy="12" r="3.2"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M4.9 4.9l2.1 2.1m10 10l2.1 2.1m0-14.2l-2.1 2.1m-10 10l-2.1 2.1"/>'),
    'wrench': _ic('<path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6l-2.8 2.8-2.5-.7-.7-2.5 3-2.6z"/>'),
    'chip': _ic('<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10-2l-2 2M5 19l2-2m10 2l-2-2"/>'),
    'shield': _ic('<path d="M12 3l7 3v5c0 5-3.5 8-7 9-3.5-1-7-4-7-9V6l7-3z"/><path d="M9.5 12l2 2 3.5-4"/>'),
    'arrow': _ic('<path d="M5 12h14m-6-6l6 6-6 6"/>'),
    'check': _ic('<path d="M4.5 12.5l5 5 10-11"/>'),
    'phone': _ic('<path d="M5 4h4l2 5-2.5 1.5a12 12 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>'),
    'mail': _ic('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'),
    'pin': _ic('<path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.6"/>'),
    'clock': _ic('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
    'chevron': _ic('<path d="M6 9l6 6 6-6"/>'),
    'ruler': _ic('<path d="M3 17L17 3l4 4L7 21l-4-4z"/><path d="M8 12l1.5 1.5M11 9l1.5 1.5M14 6l1.5 1.5"/>'),
    'bulb': _ic('<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.8.6 1.5 1.6 1.5 2.6h4c0-1 .7-2 1.5-2.6A6 6 0 0 0 12 3z"/>'),
    'truck': _ic('<path d="M2 6h12v10H2zM14 10h4l4 4v2h-8z"/><circle cx="6.5" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/>'),
}

# ---------------- SEO head ----------------
ORG_JSONLD = '''{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "R.A.P MOULD (Rahkar Andishan Pars Ghaleb)",
  "alternateName": "Rahkar Andishan Pars Ghaleb",
  "url": "%(base)s/",
  "slogan": "Precision Mold Design & Manufacturing",
  "description": "R.A.P MOULD designs and manufactures precision industrial molds, plastic injection, die-cast, press and progressive molds, backed by 40+ years of engineering experience.",
  "foundingDate": "2019",
  "email": "%(email)s",
  "telephone": "+98-919-960-5799",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Bojnord",
    "addressRegion": "North Khorasan",
    "addressCountry": "IR"
  }
}''' % {'base': SITE['base_url'], 'email': SITE['email1']}

def faq_jsonld(faqs):
    items = []
    for q, a in faqs:
        items.append('{"@type": "Question", "name": %s, "acceptedAnswer": {"@type": "Answer", "text": %s}}'
                     % (json_str(q), json_str(a)))
    return '{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [%s]}' % ','.join(items)

def json_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'

def breadcrumb_jsonld(trail):
    items = []
    for i, (name, path) in enumerate(trail, 1):
        items.append('{"@type": "ListItem", "position": %d, "name": %s, "item": "%s%s"}'
                     % (i, json_str(name), SITE['base_url'], path))
    return '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [%s]}' % ','.join(items)

def service_jsonld(name, desc, path):
    return ('{"@context": "https://schema.org", "@type": "Service", '
            '"name": %s, "description": %s, "url": "%s%s", '
            '"provider": {"@type": "Organization", "name": "R.A.P MOULD", "url": "%s/"}, '
            '"areaServed": "Worldwide"}'
            % (json_str(name), json_str(desc), SITE['base_url'], path, SITE['base_url']))

def head(page, extra_jsonld=None):
    canon = SITE['base_url'] + page['path']
    jlds = [ORG_JSONLD]
    if extra_jsonld:
        jlds.extend(extra_jsonld if isinstance(extra_jsonld, list) else [extra_jsonld])
    jld_tags = '\n'.join('<script type="application/ld+json">\n%s\n</script>' % j for j in jlds)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page['title']}</title>
<meta name="description" content="{page['desc']}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="R.A.P MOULD">
<meta property="og:title" content="{page['title']}">
<meta property="og:description" content="{page['desc']}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE['base_url']}/assets/img/og-cover.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/main.css">
{jld_tags}
</head>'''

# ---------------- header / footer ----------------
def header(active_path):
    caret = ICONS['chevron'].replace('<svg', '<svg class="caret"')
    links = []
    for path, label in NAV:
        if path == '/services/':
            items = '\n'.join(
                f'<li><a href="/services/{s}/"><strong>{n}</strong><span>{d}</span></a></li>'
                for s, n, _, d in SERVICES)
            active = ' active' if active_path.startswith('/services/') else ''
            links.append(
                f'<li class="has-dropdown"><a class="nav-link{active}" href="/services/" aria-haspopup="true">Services {caret}</a>'
                f'<ul class="dropdown">{items}</ul></li>')
        else:
            cls = ' active' if (path == '/' and active_path == '/') or (path != '/' and active_path.startswith(path)) else ''
            links.append(f'<li><a class="nav-link{cls}" href="{path}">{label}</a></li>')
    return f'''
<div class="topbar"><div class="container">
  <span class="item">{ICONS["phone"]}<a href="tel:{SITE["phone1_href"]}">{SITE["phone1"]}</a></span>
  <span class="item">{ICONS["mail"]}<a href="mailto:{SITE["email1"]}">{SITE["email1"]}</a></span>
</div></div>
<header class="site-header"><div class="container navbar">
  <a class="brand" href="/" aria-label="R.A.P MOULD home">
    <img class="brand-logo" src="/assets/img/logo-blue.svg" alt="R.A.P MOULD" width="105" height="46">
    <span class="brand-text"><small>Rahkar Andishan Pars Ghaleb</small></span>
  </a>
  <nav aria-label="Primary"><ul class="nav-links">{''.join(links)}</ul></nav>
  <div class="nav-cta">
    <a class="btn btn-primary btn-sm" href="/contact/">Request a Quote</a>
    <button class="burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</div></header>'''

def footer():
    svc_links = '\n'.join(f'<li><a href="/services/{s}/">{n}</a></li>' for s, n, _, _ in SERVICES)
    return f'''
<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand">
      <a class="brand" href="/" aria-label="R.A.P MOULD home">
        <img class="brand-logo" src="/assets/img/logo.svg" alt="R.A.P MOULD" width="120" height="53">
      </a>
      <p>Precision mold design and manufacturing, backed by 40+ years of engineering experience and 100+ completed projects.</p>
    </div>
    <div>
      <h4>Services</h4>
      <ul class="footer-links">{svc_links}</ul>
    </div>
    <div>
      <h4>Company</h4>
      <ul class="footer-links">
        <li><a href="/about/">About Us</a></li>
        <li><a href="/case-studies/">Case Studies</a></li>
        <li><a href="/facilities/">Facilities</a></li>
        <li><a href="/process/">Our Process</a></li>
        <li><a href="/contact/">Contact</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <ul class="footer-contact">
        <li>{ICONS["pin"]}<span>{SITE["address"]}</span></li>
        <li>{ICONS["phone"]}<span><a href="tel:{SITE["phone1_href"]}" style="color:inherit">{SITE["phone1"]}</a><br><a href="tel:{SITE["phone2_href"]}" style="color:inherit">{SITE["phone2"]}</a></span></li>
        <li>{ICONS["mail"]}<span><a href="mailto:{SITE["email1"]}" style="color:inherit">{SITE["email1"]}</a></span></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom"><div class="container">
    <span>&copy; 2026 R.A.P MOULD (Rahkar Andishan Pars Ghaleb). All rights reserved.</span>
    <span class="designed-by">Designed by <a href="https://arshiasdrl.ir" target="_blank" rel="noopener">Arshia</a></span>
  </div></div>
</div></footer>
<script src="/assets/js/main.js" defer></script>
</body>
</html>'''

# ---------------- shared blocks ----------------
def cta_band(title='Have a mold project in mind?',
             text='Send us your drawings, 3D models, or a physical sample. Our engineering team will review them and get back to you with a clear, no-obligation proposal.'):
    return f'''
<section class="section"><div class="container">
  <div class="cta-band">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div><a class="btn btn-light btn-lg" href="/contact/">Request a Quote</a></div>
  </div>
</div></section>'''

def faq_block(faqs):
    items = '\n'.join(
        f'<div class="faq-item"><button class="faq-q" aria-expanded="false">{q}<span class="plus">+</span></button><div class="faq-a"><p>{a}</p></div></div>'
        for q, a in faqs)
    return f'<div class="faq">{items}</div>'

def photo_slot(label, note, tall=False):
    cls = 'photo-slot tall' if tall else 'photo-slot'
    return f'''<div class="{cls}" role="img" aria-label="{label} (photo placeholder)">
  {ICONS["mold"]}<strong>{label}</strong><small>{note}</small></div>'''

def page_hero(crumbs, title, lead):
    trail = ' <span aria-hidden="true">/</span> '.join(
        f'<a href="{p}">{n}</a>' for n, p in crumbs)
    return f'''
<section class="page-hero"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
  <h1>{title}</h1><p>{lead}</p>
</div></section>'''

def service_cards(exclude=None):
    out = []
    for s, n, short, _ in SERVICES:
        if s == exclude: continue
        icon = {'plastic-injection-molds': 'mold', 'die-cast-molds': 'layers',
                'progressive-press-molds': 'gear', 'cnc-machining': 'ruler',
                'reverse-engineering': 'bulb', 'mold-repair-maintenance': 'wrench'}[s]
        out.append(f'''<a class="card" href="/services/{s}/">
  <span class="icon">{ICONS[icon]}</span><h3>{n}</h3><p>{short}</p>
  <span class="card-link">Learn more {ICONS["arrow"]}</span></a>''')
    return '\n'.join(out)

# ============================================================ HOME
def page_home():
    body = f'''
<section class="hero"><div class="container">
  <span class="eyebrow on-dark">R.A.P MOULD (Rahkar Andishan Pars Ghaleb)</span>
  <h1>Industrial Molds, Engineered for Serious Production</h1>
  <p class="lead">We design and manufacture precision plastic injection, die-cast, press, and progressive molds, backed by 40+ years of hands-on engineering experience and 100+ completed projects across automotive, appliance, hygiene, and packaging industries.</p>
  <div class="hero-actions">
    <a class="btn btn-light btn-lg" href="/contact/">Request a Quote</a>
    <a class="btn btn-lg" href="/services/" style="border-color:rgba(255,255,255,.5);color:#fff">Explore Services</a>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><strong><span class="count-up" data-count="40">40</span>+</strong><span>Years of engineering experience</span></div>
    <div class="hero-stat"><strong><span class="count-up" data-count="100">100</span>+</strong><span>Molds &amp; projects delivered</span></div>
    <div class="hero-stat"><strong><span class="count-up" data-count="6">6</span></strong><span>Core engineering services</span></div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head center">
    <span class="eyebrow">What we do</span>
    <h2>Complete Mold Engineering Under One Roof</h2>
    <p class="lead">From the first 3D model to the final tested mold, design, machining, assembly, and lifetime support.</p>
  </div>
  <div class="grid cols-3">{service_cards()}</div>
</div></section>

<section class="section alt"><div class="container">
  <div class="split">
    <div>
      <span class="eyebrow">Why R.A.P MOULD</span>
      <h2>Engineering Depth You Can Build Production On</h2>
      <p class="lead">Our foundation is deep technical knowledge and four decades of mold-making experience, applied directly to every key project by our senior engineer.</p>
      <ul class="checklist">
        <li><span class="tick">{ICONS["check"]}</span><span><strong>Micron-level precision</strong> in mold manufacturing and machining.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span><strong>Proven on challenging projects</strong>, 100+ successful deliveries.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span><strong>Long-life molds</strong> that reduce your production costs.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span><strong>Full transparency</strong> across design and manufacturing, with after-delivery technical support.</span></li>
      </ul>
      <div style="margin-top:28px"><a class="btn btn-outline" href="/about/">About the Company {ICONS["arrow"]}</a></div>
    </div>
    <div>{photo_slot("Workshop photo", "Replace with a real photo of the workshop or the engineering team.", tall=True)}</div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head">
    <span class="eyebrow">Selected work</span>
    <h2>Case Studies From the Shop Floor</h2>
    <p class="lead">Real projects, real constraints, measurable results.</p>
  </div>
  <div class="grid cols-3">
    <div class="card case-card"><div class="case-top"><span class="case-tag">Automotive</span><h3>Fuel Pump Mold: Capra Pickup</h3></div>
      <div class="case-body"><div class="case-row"><h4>Challenge</h4><p>Limited equipment and a highly complex product geometry.</p></div>
      <div class="case-result"><p>Result: better pricing than the Chinese reference sample.</p></div></div></div>
    <div class="card case-card"><div class="case-top"><span class="case-tag">Reverse Engineering</span><h3>Egg Tray Stand for Incubator</h3></div>
      <div class="case-body"><div class="case-row"><h4>Challenge</h4><p>Complex modeling from a physical sample with no drawings.</p></div>
      <div class="case-result"><p>Result: improved ROI through more economical production.</p></div></div></div>
    <div class="card case-card"><div class="case-top"><span class="case-tag">Heavy Tooling</span><h3>Trailer Fender Mold</h3></div>
      <div class="case-body"><div class="case-row"><h4>Challenge</h4><p>An exceptionally heavy mold project.</p></div>
      <div class="case-result"><p>Result: lower material and machining costs via cast steel.</p></div></div></div>
  </div>
  <div style="margin-top:32px;text-align:center"><a class="btn btn-outline" href="/case-studies/">View All Case Studies {ICONS["arrow"]}</a></div>
</div></section>

<section class="stats-band section"><div class="container">
  <div class="grid cols-4">
    <div class="stat"><strong><span class="count-up" data-count="40">40</span><em>+</em></strong><span>Years of engineering experience</span></div>
    <div class="stat"><strong><span class="count-up" data-count="100">100</span><em>+</em></strong><span>Projects completed</span></div>
    <div class="stat"><strong><span class="count-up" data-count="6">6</span></strong><span>Core services</span></div>
    <div class="stat"><strong><span class="count-up" data-count="5">5</span></strong><span>Specialized machines in-house</span></div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head center">
    <span class="eyebrow">How we work</span>
    <h2>A Transparent Process, From Drawing to Delivery</h2>
    <p class="lead">Six clear steps. You approve the design before we cut a single piece of steel.</p>
  </div>
  <div class="grid cols-3">
    <div class="card"><span class="num-badge">1</span><h3>Consultation</h3><p>Share drawings, 3D models, or a sample. Free expert consultation on material and method.</p></div>
    <div class="card"><span class="num-badge">2</span><h3>Design &amp; 3D Model</h3><p>Initial 3D mold design with analysis report, manufacturing starts only after your approval.</p></div>
    <div class="card"><span class="num-badge">3</span><h3>Precision Manufacturing</h3><p>CNC machining and EDM with continuous dimensional control at every stage.</p></div>
  </div>
  <div style="margin-top:32px;text-align:center"><a class="btn btn-outline" href="/process/">See the Full Process {ICONS["arrow"]}</a></div>
</div></section>
{cta_band()}'''
    return {'path': '/', 'title': 'R.A.P MOULD | Industrial Mold Design & Manufacturing',
            'desc': 'R.A.P MOULD designs and builds precision plastic injection, die-cast, press and progressive molds. 40+ years of engineering experience, 100+ projects delivered.',
            'body': body, 'jsonld': None}

# ============================================================ ABOUT
def page_about():
    body = f'''
{page_hero([("Home", "/"), ("About Us", "/about/")], "About R.A.P MOULD",
           "A mold engineering company built on four decades of hands-on experience, where every key project is guided directly by a senior mold engineer.")}

<section class="section"><div class="container">
  <div class="split">
    <div class="prose">
      <span class="eyebrow">Our story</span>
      <h2>Founded on Engineering, Driven by Precision</h2>
      <p>Rahkar Andishan Pars Ghaleb (R.A.P MOULD) was founded in 2019 to bring a new standard of service to industrial mold design and engineering. Our credibility rests on something no marketing can buy: deep technical knowledge and more than forty years of engineering experience in the mold-making industry, earned by Mr. Davoud Sadr al-Zakerin across 100+ diverse, successfully completed projects.</p>
      <p>We combine the experience of generations with current methods and technologies to deliver innovative, optimized solutions for our customers' most complex production challenges.</p>
      <p><strong>Our mission goes beyond building molds.</strong> By deeply understanding production processes and each industry's unique needs, we create lasting value and competitive advantage for our business partners. Uncompromising precision, superior quality, and on-time delivery are the pillars of our work, and your guarantee of satisfaction.</p>
    </div>
    <div>{photo_slot("Founder portrait", "Replace with a professional portrait of the founder/engineer.", tall=True)}</div>
  </div>
</div></section>

<section class="section alt"><div class="container">
  <span class="eyebrow">The engineer behind the molds</span>
  <h2 style="margin-bottom:32px">Davoud Sadr al-Zakerin</h2>
  <div class="grid cols-2">
    <div class="card">
      <h3>Profile</h3>
      <p style="margin-top:10px">Mold engineer with 40+ years of specialized experience in the design, manufacturing, and optimization of industrial molds, plastic injection, die-cast, and press tooling, for automotive parts, home appliances, hygiene and cosmetic products, electrical and agricultural equipment, parts manufacturing, and machine building. A track record of managing and executing 100+ complex projects, focused on innovation, high precision, and production efficiency.</p>
      <dl class="kv" style="margin-top:20px">
        <dt>Email</dt><dd><a href="mailto:{SITE["email1"]}">{SITE["email1"]}</a><br><a href="mailto:{SITE["email2"]}">{SITE["email2"]}</a></dd>
        <dt>Phone</dt><dd><a href="tel:{SITE["phone1_href"]}">{SITE["phone1"]}</a><br><a href="tel:{SITE["phone2_href"]}">{SITE["phone2"]}</a></dd>
      </dl>
    </div>
    <div class="card">
      <h3>Education &amp; Honors</h3>
      <ul class="checklist">
        <li><span class="tick">{ICONS["check"]}</span><span>18-month Grade-1 Iran–Germany technical program in machine tools &amp; mold making (1991–1993).</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>First place, national technical skills competitions (1993 &amp; 1997).</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Specialist certification in EDM (spark machining).</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Six-month welding inspection certification, Karaj House of Industry &amp; Mine.</span></li>
      </ul>
    </div>
  </div>
  <div class="grid cols-2" style="margin-top:24px">
    <div class="card">
      <h3>Career Highlights</h3>
      <ul class="checklist">
        <li><span class="tick">{ICONS["check"]}</span><span>Designed and built cylinder boring machines for industrial clients in Bojnord.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Designed and manufactured 100+ plastic injection molds for automotive, appliance, hygiene, cosmetic, electrical, and agricultural industries, plus closure molds.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Supervised mold-making units at five manufacturing companies.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Designed and built a gearbox mold for the food and hygiene industries.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Maintenance engineering expert; designed and built a polymer melting machine for two industrial firms.</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Technical Skills</h3>
      <div style="margin-top:14px">
        <div class="skill"><div class="skill-top"><span>Manual Machines</span><span>10/10</span></div><div class="skill-bar"><div class="skill-fill" style="width:100%"></div></div></div>
        <div class="skill"><div class="skill-top"><span>EDM (Spark Machining)</span><span>10/10</span></div><div class="skill-bar"><div class="skill-fill" style="width:100%"></div></div></div>
        <div class="skill"><div class="skill-top"><span>SolidWorks</span><span>8/10</span></div><div class="skill-bar"><div class="skill-fill" style="width:80%"></div></div></div>
        <div class="skill"><div class="skill-top"><span>Reverse Engineering</span><span>7/10</span></div><div class="skill-bar"><div class="skill-fill" style="width:70%"></div></div></div>
        <div class="skill"><div class="skill-top"><span>Process Planning &amp; Documentation</span><span>7/10</span></div><div class="skill-bar"><div class="skill-fill" style="width:70%"></div></div></div>
      </div>
    </div>
  </div>
</div></section>
{cta_band()}'''
    return {'path': '/about/', 'title': 'About Us | R.A.P MOULD',
            'desc': 'R.A.P MOULD was founded in 2019 on 40+ years of mold engineering experience. Meet Davoud Sadr al-Zakerin and the team behind 100+ completed mold projects.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('About Us', '/about/')])]}

# ============================================================ SERVICES HUB
def page_services():
    body = f'''
{page_hero([("Home", "/"), ("Services", "/services/")], "Our Services",
           "Six engineering services covering the full life of an industrial mold, from first sketch to long-term maintenance.")}

<section class="section"><div class="container">
  <div class="grid cols-3">{service_cards()}</div>
</div></section>

<section class="section alt"><div class="container">
  <div class="section-head">
    <span class="eyebrow">Industries we serve</span>
    <h2>Tooling for Demanding Industries</h2>
    <p class="lead">Our molds run in production lines across a wide range of sectors.</p>
  </div>
  <ul class="pill-list">
    <li>Automotive parts</li><li>Home appliances</li><li>Hygiene &amp; cosmetics</li>
    <li>Electrical equipment</li><li>Agricultural machinery</li><li>Food &amp; packaging</li>
    <li>Parts manufacturing</li><li>Machine building</li>
  </ul>
</div></section>
{cta_band('Not sure which service you need?',
          'Describe your part or send a sample, we will recommend the right mold type, material, and manufacturing method, free of charge.')}'''
    return {'path': '/services/', 'title': 'Mold Engineering Services | R.A.P MOULD',
            'desc': 'Mold design, plastic injection & die-cast mold manufacturing, CNC machining, reverse engineering, and mold repair, six engineering services from R.A.P MOULD.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Services', '/services/')])]}

# ============================================================ SERVICE DETAIL PAGES
SERVICE_DATA = {
 'plastic-injection-molds': {
   'name': 'Plastic Injection Molds',
   'short': 'Custom plastic injection molds designed and built for precision, longevity, and economical production.',
   'desc': 'Custom plastic injection mold design and manufacturing for automotive, appliance, hygiene and packaging parts.',
   'intro': ('We design and manufacture custom plastic injection molds for parts that must run reliably, shift after shift. '
             'Every mold is engineered around your part geometry, resin, and production volume, with cooling, ejection, and gating designed for cycle efficiency and part quality.'),
   'includes': [
     'Complete mold design with 3D modeling and mold-flow-minded engineering',
     'Single and multi-cavity molds for thermoplastic parts',
     'Hot-runner and cold-runner systems, engineered for your resin',
     'Precision core, cavity, and insert machining with EDM finishing',
     'Assembly, fitting, and trial testing before delivery',
   ],
   'industries': ['Automotive parts', 'Home appliances', 'Hygiene & cosmetics', 'Electrical components', 'Caps & closures', 'Agricultural parts'],
   'faqs': [
     ('What do you need from us to start?', 'Ideally a 3D model (STEP/IGES) or 2D drawings of the part, plus the resin type and expected annual volume. A physical sample also works, we can reverse-engineer it.'),
     ('How long does an injection mold take?', 'Lead time depends on size and complexity. After design approval, a typical single-cavity mold takes a few weeks; we give you a firm schedule with your quote.'),
     ('Do you test the mold before delivery?', 'Yes. Every mold is assembled and trial-tested so you receive tooling that is proven to run, along with the test report.'),
   ]},
 'die-cast-molds': {
   'name': 'Die-Cast Molds',
   'short': 'High-pressure die-cast molds built for dimensional stability and long production runs.',
   'desc': 'High-pressure die-cast mold design and manufacturing for dimensionally stable, high-volume metal parts.',
   'intro': ('Our die-cast molds are built to withstand the thermal and mechanical demands of high-pressure die casting. '
             'We engineer proper thermal management, venting, and overflow systems so your parts come out dense, dimensionally stable, and ready for finishing.'),
   'includes': [
     'Die-cast mold design with thermal and gating analysis',
     'H13 and premium hot-work tool steels, heat-treated to spec',
     'Precision machining with EDM for complex geometries',
     'Cooling channel design for cycle time and die life',
     'Assembly, trial casting support, and dimensional verification',
   ],
   'industries': ['Automotive parts', 'Electrical housings', 'Machine building', 'Agricultural machinery'],
   'faqs': [
     ('Which alloys are your molds suited for?', 'Our die-cast tooling is designed around common aluminum and zinc alloys. Tell us your alloy and we engineer the steel selection and thermal design accordingly.'),
     ('Can you handle complex geometries?', 'Yes, EDM (spark) machining lets us produce intricate cores and cavities that conventional milling cannot reach.'),
     ('Do you support the first production trials?', 'Yes. We support trial runs and fine-tune the mold based on casting results before final handover.'),
   ]},
 'progressive-press-molds': {
   'name': 'Press & Progressive Molds',
   'short': 'Metal press and progressive (staged) molds for efficient, high-volume sheet-metal forming.',
   'desc': 'Metal press and progressive mold design and manufacturing for efficient sheet-metal part production.',
   'intro': ('From single-stage press tools to fully progressive (staged) dies, we build sheet-metal tooling that forms accurately and lasts. '
             'Strip layout and station design are optimized to minimize scrap and maximize press strokes per minute.'),
   'includes': [
     'Single-stage and progressive die design with strip layout optimization',
     'Blanking, piercing, bending, drawing, and forming stations',
     'Precision-ground die components with proper clearances per material',
     'Tryout, adjustment, and first-article verification',
   ],
   'industries': ['Automotive parts', 'Electrical components', 'Home appliances', 'Machine building'],
   'faqs': [
     ('Single-stage or progressive, which do I need?', 'It depends on part complexity and volume. Progressive dies pay off at higher volumes; single-stage tools are economical for simpler parts and lower runs. We advise you honestly after reviewing the part.'),
     ('What sheet materials can you tool for?', 'Common mild steels, stainless, aluminum, copper, and brass. Material thickness and grade drive the clearance and steel selection.'),
   ]},
 'cnc-machining': {
   'name': 'CNC Machining',
   'short': 'High-accuracy turning and milling for mold components and industrial parts.',
   'desc': 'Precision CNC turning and milling services for mold components and industrial parts.',
   'intro': ('Our machining services support both our own mold builds and standalone customer orders. '
             'Tight tolerances, documented dimensions, and consistent finishes, whether you need a single replacement insert or a batch of precision components.'),
   'includes': [
     'CNC turning and milling to tight tolerances',
     'Mold components: cores, cavities, inserts, ejector systems',
     'One-off prototypes through small-batch production',
     'Dimensional control and documentation with every order',
   ],
   'industries': ['Mold making', 'Machine building', 'Parts manufacturing', 'Agricultural machinery'],
   'faqs': [
     ('Can you machine from our drawings or models?', 'Yes, send 2D drawings or 3D models (STEP/IGES). We confirm tolerances and material before quoting.'),
     ('What is your typical tolerance capability?', 'We routinely hold tight tolerances on mold components; exact capability depends on geometry and material, ask us about your specific part.'),
   ]},
 'reverse-engineering': {
   'name': 'Reverse Engineering',
   'short': 'From a worn part or sample to production-ready 3D models and tooling.',
   'desc': 'Reverse engineering services: from physical samples to 3D models, drawings, and new tooling.',
   'intro': ('No drawings? No problem. We measure and model physical parts, even worn or damaged ones, and rebuild them as accurate 3D models, '
             'technical drawings, and, when needed, brand-new molds. It is the fastest route from a legacy part back into production.'),
   'includes': [
     'Precision measurement of physical samples (manual + instrument-aided)',
     'Parametric 3D modeling in SolidWorks',
     'Technical drawings with tolerances and material specs',
     'Design improvements for manufacturability where useful',
     'New mold manufacturing from the rebuilt model',
   ],
   'industries': ['Parts manufacturing', 'Agricultural machinery', 'Home appliances', 'Machine building'],
   'faqs': [
     ('The original part is worn, can you still model it?', 'Yes. We account for wear during measurement and rebuild the part to its intended nominal geometry, confirming critical dimensions with you.'),
     ('Can you improve the design, not just copy it?', 'Absolutely. Reverse engineering is often the right moment to fix weak points, improve draft angles, or simplify manufacturing, we propose options before modeling.'),
   ]},
 'mold-repair-maintenance': {
   'name': 'Mold Repair & Maintenance',
   'short': 'Expert repair, refurbishment, and preventive care that keeps your molds running.',
   'desc': 'Mold repair, refurbishment, and preventive maintenance to extend tool life and cut downtime.',
   'intro': ('A well-maintained mold produces for years; a neglected one fails mid-run. We repair damaged molds, refurbish worn tooling, '
             'and set up preventive maintenance routines that protect your production schedule and your investment.'),
   'includes': [
     'Diagnosis of mold damage, wear, and failure causes',
     'Welding, re-machining, and polishing of damaged areas',
     'Replacement of worn components (ejectors, inserts, cooling parts)',
     'Refurbishment programs to restore molds to production condition',
     'Preventive maintenance guidance and schedules',
   ],
   'industries': ['Plastics production', 'Automotive parts', 'Packaging', 'Home appliances'],
   'faqs': [
     ('Can you repair a mold built by another shop?', 'In most cases, yes. We assess the damage first and give you an honest verdict on whether repair is economical versus rebuilding.'),
     ('How fast is emergency repair?', 'Tell us it is urgent when you contact us, rush repairs are prioritized and we keep you updated at every stage.'),
   ]},
}

SERVICE_ICON = {'plastic-injection-molds': 'mold', 'die-cast-molds': 'layers',
                'progressive-press-molds': 'gear', 'cnc-machining': 'ruler',
                'reverse-engineering': 'bulb', 'mold-repair-maintenance': 'wrench'}

def page_service(slug):
    d = SERVICE_DATA[slug]
    faqs = d['faqs']
    others = [(s, n) for s, n, _, _ in SERVICES if s != slug][:3]
    body = f'''
{page_hero([("Home", "/"), ("Services", "/services/"), (d["name"], f"/services/{slug}/")], d["name"], d["short"])}

<section class="section"><div class="container">
  <div class="split">
    <div class="prose">
      <span class="eyebrow">Service</span>
      <h2>What We Deliver</h2>
      <p>{d["intro"]}</p>
      <ul class="checklist">
        {''.join(f'<li><span class="tick">{ICONS["check"]}</span><span>{i}</span></li>' for i in d["includes"])}
      </ul>
    </div>
    <div>{photo_slot(d["name"] + ", photo", "Replace with a real photo: the mold, the machine, or parts it produces.", tall=True)}</div>
  </div>
</div></section>

<section class="section alt"><div class="container">
  <div class="section-head">
    <span class="eyebrow">Typical applications</span>
    <h2>Industries We Serve With This Service</h2>
  </div>
  <ul class="pill-list">{''.join(f'<li>{i}</li>' for i in d["industries"])}</ul>
  <div class="divider"></div>
  <div class="section-head">
    <span class="eyebrow">Common questions</span>
    <h2>FAQ</h2>
  </div>
  {faq_block(faqs)}
</div></section>

<section class="section"><div class="container">
  <div class="section-head">
    <span class="eyebrow">Keep exploring</span>
    <h2>Related Services</h2>
  </div>
  <div class="grid cols-3">
    {''.join(f'<a class="card" href="/services/{s}/"><span class="icon">{ICONS[SERVICE_ICON[s]]}</span><h3>{n}</h3><span class="card-link">Learn more {ICONS["arrow"]}</span></a>' for s, n in others)}
  </div>
</div></section>
{cta_band()}'''
    return {'path': f'/services/{slug}/', 'title': f'{d["name"]} | R.A.P MOULD',
            'desc': d['desc'],
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Services', '/services/'), (d['name'], f'/services/{slug}/')]),
                       service_jsonld(d['name'], d['short'], f'/services/{slug}/'),
                       faq_jsonld(faqs)]}

# ============================================================ CASE STUDIES
CASES = [
 ('Automotive', 'Fuel Pump Mold: Capra Pickup', 'Tat Plastic',
  'Limited workshop equipment combined with a highly complex product geometry.',
  'Designed an alternative manufacturing process using the equipment available, without compromising the design intent.',
  'Better pricing than the Chinese reference sample, with local support.'),
 ('Reverse Engineering', 'Egg Tray Stand for Incubator', 'Private client',
  'Complex modeling required from a physical sample, with no drawings available.',
  'Reverse engineering with precise manual measurement, rebuilt as a production-ready 3D model.',
  'Improved return on investment through more economical production.'),
 ('Heavy Tooling', 'Trailer Fender Mold', 'Private client',
  'An exceptionally heavy mold project with significant material costs.',
  'Used cast steel instead of a solid steel block for the mold body.',
  'Reduced raw material and machining costs while meeting strength requirements.'),
 ('Precision Molding', 'Washing-Machine Detergent Cap Mold', 'Private client',
  'A delicate part demanding fine detail in both part and mold design.',
  'Applied 40 years of mold-making experience with EDM finishing for intricate details.',
  'Clean, flash-free parts straight from the first trials.'),
 ('Machine Building', 'Cylinder Boring Machine (Design & Build)', 'Eyni Sanat Bojnord',
  'Designing a machine from zero, with no existing prototype to reference.',
  'Functional analysis followed by gradual prototyping and refinement.',
  'Lower build cost than comparable machines on the market.'),
]

def page_cases():
    cards = '\n'.join(f'''<div class="card case-card">
  <div class="case-top"><span class="case-tag">{tag}</span><h3>{title}</h3>
  <p style="font-size:.9rem;color:var(--ink-mute);margin-top:6px">Client: {client}</p></div>
  <div class="case-body">
    <div class="case-row"><h4>Challenge</h4><p>{ch}</p></div>
    <div class="case-row"><h4>Solution</h4><p>{sol}</p></div>
    <div class="case-result"><p>{res}</p></div>
  </div></div>''' for tag, title, client, ch, sol, res in CASES)
    body = f'''
{page_hero([("Home", "/"), ("Case Studies", "/case-studies/")], "Case Studies",
           "A selection of projects from our workshop, the challenge, the engineering answer, and the result.")}

<section class="section"><div class="container">
  <div class="grid cols-2">{cards}</div>
  <p class="form-note" style="margin-top:28px">Project names and details are shared with client permission. More case studies are documented on request.</p>
</div></section>
{cta_band('Have a similar challenge?',
          'Send us your part or your problem, we will tell you honestly whether we can solve it, and how.')}'''
    return {'path': '/case-studies/', 'title': 'Case Studies | R.A.P MOULD',
            'desc': 'Real mold engineering projects: challenges, solutions, and results from the R.A.P MOULD workshop.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Case Studies', '/case-studies/')])]}

# ============================================================ FACILITIES
MACHINES = [
 ('01', '1-Meter Lathe', 'Tabriz', 'Turning of mold plates, round components, and shafts up to 1 meter.'),
 ('02', 'Turret Milling Machine FP4M', 'Tabriz', 'Precision milling of mold cavities, cores, and complex geometries.'),
 ('03', 'Column Drill 32', 'Tabriz', 'Drilling and tapping operations up to 32 mm capacity.'),
 ('04', 'Shaping Machine 40 cm', '-', 'Shaping and slotting operations for mold components.'),
 ('05', 'EDM (Spark) Machine 110 A', 'Pars Raad', 'Spark erosion for intricate details, sharp corners, and hardened steels.'),
]

def page_facilities():
    rows = '\n'.join(f'<tr><td><strong>{n}</strong></td><td>{m}</td><td>{mk}</td><td>{d}</td></tr>'
                     for n, m, mk, d in MACHINES)
    body = f'''
{page_hero([("Home", "/"), ("Facilities", "/facilities/")], "Machinery & Facilities",
           "The machines behind our molds, in-house capacity for turning, milling, drilling, shaping, and spark erosion.")}

<section class="section"><div class="container">
  <div class="section-head">
    <span class="eyebrow">In-house capacity</span>
    <h2>Our Machinery</h2>
    <p class="lead">Owning our core machines means full control over quality, scheduling, and cost.</p>
  </div>
  <div class="table-wrap"><table class="spec">
    <thead><tr><th>No.</th><th>Machine</th><th>Make</th><th>Capability</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div></section>

<section class="section alt"><div class="container">
  <div class="split">
    <div class="prose">
      <span class="eyebrow">Quality in process</span>
      <h2>Controlled at Every Stage</h2>
      <p>Dimensions and tolerances are checked and recorded continuously during manufacturing, not just at the end. Combined with EDM finishing for the details milling cannot reach, this is how we hold micron-level precision across every mold we deliver.</p>
      <ul class="checklist">
        <li><span class="tick">{ICONS["check"]}</span><span>Continuous dimensional control during machining.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>EDM for intricate geometries and hardened steels.</span></li>
        <li><span class="tick">{ICONS["check"]}</span><span>Final inspection of mold and molded parts before delivery.</span></li>
      </ul>
    </div>
    <div>{photo_slot("Workshop photo", "Replace with a real photo of the workshop floor and machines.", tall=True)}</div>
  </div>
</div></section>
{cta_band()}'''
    return {'path': '/facilities/', 'title': 'Machinery & Facilities | R.A.P MOULD',
            'desc': 'Inside the R.A.P MOULD workshop: lathe, milling, drilling, shaping and EDM machines for precision mold manufacturing.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Facilities', '/facilities/')])]}

# ============================================================ PROCESS
STEPS = [
 ('01', 'Initial Information & Free Consultation',
  'You share drawings, 3D models, technical specs, or a physical sample of the part you need.',
  ['You provide drawings, 3D models, or a physical sample',
   'Free expert consultation on the best material, manufacturing technology, and mold design']),
 ('02', 'Design, 3D Modeling & Analysis',
  'Based on your input and our consultation, we prepare the initial 3D mold design.',
  ['Initial 3D mold design prepared from your data',
   'Design and analysis report sent for your review, manufacturing begins only after your final approval']),
 ('03', 'Build Planning & Material Sourcing',
  'With an approved design, we plan the build and source everything the mold needs.',
  ['Detailed bill of materials and required components',
   'Raw materials selected and sourced to the highest quality standards']),
 ('04', 'Precision Manufacturing & Machining',
  'Mold components are machined with high precision using CNC and advanced techniques.',
  ['Planned production and machining path for every component',
   'CNC turning, milling, and EDM (spark) machining',
   'Dimensions and tolerances controlled and recorded continuously during manufacturing']),
 ('05', 'Assembly, Testing & Final Quality Control',
  'Components are assembled with precision and the mold is tested on the relevant machine.',
  ['High-precision assembly of all components',
   'Trial runs to verify performance, part quality, and drawing conformity',
   'Fast, precise corrections if optimization is needed, then final QC inspection']),
 ('06', 'Delivery & Support',
  'The approved mold is packed safely and delivered as agreed, and we stay with you.',
  ['Safe packaging and delivery per agreement',
   'Final drawings, test report, and maintenance instructions included',
   'Ongoing technical support for your production process']),
]

def page_process():
    steps = '\n'.join(f'''<div class="step"><div class="step-num">{n}</div>
  <h3>{t}</h3><p>{p}</p><ul>{''.join(f'<li>{i}</li>' for i in items)}</ul></div>'''
                      for n, t, p, items in STEPS)
    faqs = [
      ('How long does the whole process take?',
       'It depends on mold size and complexity. You receive a firm schedule with your quote, and we update you at every stage, design approval, machining, testing, delivery.'),
      ('Can I follow the progress of my mold?',
       'Yes. We believe in full transparency: you approve the 3D design before manufacturing, and we keep you informed through machining and testing.'),
      ('What if the mold needs adjustments after testing?',
       'Adjustments based on trial results are part of the process. We correct quickly and precisely, then re-verify before final delivery.'),
    ]
    body = f'''
{page_hero([("Home", "/"), ("Our Process", "/process/")], "Our Process",
           "Six transparent steps from your first drawing to a production-ready mold, with your approval gating every critical stage.")}

<section class="section"><div class="container">
  <div class="timeline">{steps}</div>
</div></section>

<section class="section alt"><div class="container">
  <div class="section-head"><span class="eyebrow">Common questions</span><h2>Process FAQ</h2></div>
  {faq_block(faqs)}
</div></section>
{cta_band('Ready to start step one?',
          'Send your drawings or sample today and receive a free engineering consultation.')}'''
    return {'path': '/process/', 'title': 'Our Process: From Drawing to Delivery | R.A.P MOULD',
            'desc': 'How R.A.P MOULD works: consultation, 3D design & approval, material sourcing, precision machining, testing, delivery and support.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Our Process', '/process/')]),
                       faq_jsonld(faqs)]}

# ============================================================ CONTACT
def page_contact():
    body = f'''
{page_hero([("Home", "/"), ("Contact", "/contact/")], "Contact Us",
           "Tell us about your project, drawings, 3D models, or just an idea. We reply within one business day.")}

<section class="section"><div class="container">
  <div class="grid cols-2" style="align-items:start">
    <div>
      <span class="eyebrow">Request a quote</span>
      <h2 style="margin-bottom:12px">Send Us a Message</h2>
      <p class="lead" style="margin-bottom:28px">Fill in the form and our engineering team will get back to you. For large files (3D models, drawings), mention them in your message and we will arrange a transfer.</p>
      <div id="form-status" class="form-status" role="status" aria-live="polite"></div>
      <form id="contact-form" class="form-grid" novalidate>
        <div class="form-row">
          <div class="field">
            <label for="cf-name">Your name <span class="req">*</span></label>
            <input id="cf-name" name="name" type="text" autocomplete="name" placeholder="John Smith" required>
            <p class="err-msg">Please enter your name.</p>
          </div>
          <div class="field">
            <label for="cf-email">Email address <span class="req">*</span></label>
            <input id="cf-email" name="email" type="email" autocomplete="email" placeholder="you@company.com" required>
            <p class="err-msg">Please enter a valid email address.</p>
          </div>
        </div>
        <div class="field">
          <label for="cf-subject">Subject</label>
          <input id="cf-subject" name="subject" type="text" placeholder="e.g. Plastic injection mold for automotive part">
        </div>
        <div class="field">
          <label for="cf-message">Your message <span class="req">*</span></label>
          <textarea id="cf-message" name="message" placeholder="Describe your part, material, quantities, timeline..." required></textarea>
          <p class="err-msg">Please write at least a few words about your project.</p>
        </div>
        <div class="field hp" aria-hidden="true">
          <label for="cf-website">Website</label>
          <input id="cf-website" name="website" type="text" tabindex="-1" autocomplete="off">
        </div>
        <div class="field">
          <div class="cf-turnstile" data-sitekey="{SITE['turnstile_site_key']}" data-theme="light"></div>
          <p class="err-msg" id="cf-captcha-err">Please complete the captcha verification.</p>
        </div>
        <div>
          <button type="submit" class="btn btn-primary btn-lg">Send Message</button>
          <p class="form-note" style="margin-top:12px">Prefer email? Write to us directly at <a href="mailto:{SITE["email1"]}">{SITE["email1"]}</a></p>
        </div>
      </form>
    </div>
    <div>
      <div class="card" style="margin-bottom:24px">
        <h3>Contact Details</h3>
        <ul class="footer-contact" style="margin-top:16px;color:var(--ink-soft)">
          <li>{ICONS["pin"]}<span>{SITE["address"]}</span></li>
          <li>{ICONS["phone"]}<span><a href="tel:{SITE["phone1_href"]}">{SITE["phone1"]}</a><br><a href="tel:{SITE["phone2_href"]}">{SITE["phone2"]}</a></span></li>
          <li>{ICONS["mail"]}<span><a href="mailto:{SITE["email1"]}">{SITE["email1"]}</a><br><a href="mailto:{SITE["email2"]}">{SITE["email2"]}</a></span></li>
          <li>{ICONS["clock"]}<span>Replies within one business day</span></li>
        </ul>
      </div>
      {photo_slot("Map / location", "Embed a map or add a photo of the workshop exterior here.")}
    </div>
  </div>
</div></section>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>'''
    return {'path': '/contact/', 'title': 'Contact Us: Request a Quote | R.A.P MOULD',
            'desc': 'Contact R.A.P MOULD for mold design and manufacturing quotes. Send drawings or a message, we reply within one business day.',
            'body': body,
            'jsonld': [breadcrumb_jsonld([('Home', '/'), ('Contact', '/contact/')])]}

# ============================================================ REGISTRY + BUILD
def all_pages():
    pages = [page_home(), page_about(), page_services()]
    pages += [page_service(s) for s, _, _, _ in SERVICES]
    pages += [page_cases(), page_facilities(), page_process(), page_contact()]
    return pages

def render(page):
    return (head(page, page.get('jsonld'))
            + '<body>' + header(page['path'])
            + '<main>' + page['body'] + '</main>'
            + footer())

def write_page(page):
    rel = page['path'].lstrip('/')
    outdir = os.path.join(DIST, rel)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render(page))
    return page['path']

def write_sitemap(paths):
    urls = '\n'.join(
        f'  <url><loc>{SITE["base_url"]}{p}</loc><changefreq>{"weekly" if p == "/" else "monthly"}</changefreq><priority>{"1.0" if p == "/" else "0.8"}</priority></url>'
        for p in paths)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
'''
    with open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(xml)

def write_robots():
    with open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE["base_url"]}/sitemap.xml\n')

def write_404():
    body = '''
<section class="section"><div class="container" style="text-align:center;padding:60px 0">
  <span class="eyebrow">Error 404</span>
  <h1>Page Not Found</h1>
  <p class="lead" style="margin:16px auto 32px">The page you are looking for does not exist or has been moved.</p>
  <a class="btn btn-primary" href="/">Back to Home</a>
</div></section>'''
    page = {'path': '/404.html', 'title': 'Page Not Found | R.A.P MOULD',
            'desc': 'The requested page could not be found.', 'body': body}
    with open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8') as f:
        f.write(head(page, None) + '<body>' + header('/') + '<main>' + body + '</main>' + footer())

def main():
    # keep dist/assets, functions; wipe generated html/xml/txt
    for name in os.listdir(DIST):
        p = os.path.join(DIST, name)
        if name == 'assets':
            continue
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
    pages = all_pages()
    paths = [write_page(p) for p in pages]
    write_sitemap(paths)
    write_robots()
    write_404()
    print(f'Built {len(paths)} pages:')
    for p in paths:
        print(' ', p)
    print(' + /sitemap.xml  /robots.txt  /404.html')

if __name__ == '__main__':
    main()

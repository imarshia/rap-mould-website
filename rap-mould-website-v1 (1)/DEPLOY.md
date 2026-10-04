# R.A.P MOULD — Deploy Guide (Cloudflare Pages)

## What you have
- `dist/` — the built static site (13 pages). This is what gets deployed.
- `src/build.py` — single-source generator. Edit content here, then run `python3 src/build.py` to rebuild `dist/`.
- `functions/api/contact.js` — Pages Function that receives the contact form and emails it via MailChannels.

## 1. Push to GitHub
```bash
cd ~/workspace/rap-mould
git init && git add -A && git commit -m "R.A.P MOULD website v1"
# create a repo on GitHub, then:
git remote add origin <your-repo-url>
git push -u origin main
```

## 2. Create the Pages project
1. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git.
2. Select the repo. Build settings:
   - Build command: `python3 src/build.py`
   - Build output directory: `dist`
3. Deploy. You get `*.pages.dev` instantly.

## 3. Contact form → email setup (one-time)
The form POSTs to `/api/contact`, which sends via **MailChannels** (free, no signup).
Spam protection is three-layered: honeypot field + **Cloudflare Turnstile captcha**
(verified server-side, fail-closed) + field validation.

a) Turnstile keys (Cloudflare dashboard → Turnstile → Add site):
   - Add your domain (e.g. `rapmould.com`), widget mode "Managed" is fine.
   - Copy the **Site Key** → put it in `src/build.py` as `turnstile_site_key`
     (replacing `YOUR_TURNSTILE_SITE_KEY`), then rebuild: `python3 src/build.py`.
   - Copy the **Secret Key** → Pages → your project → Settings →
     Environment variables → add `TURNSTILE_SECRET_KEY`.

b) Pages → your project → Settings → Environment variables → add:
   - `MAIL_FROM` = `website@YOURDOMAIN` (must be an address on YOUR domain, e.g. `website@rapmould.com`)
   - `MAIL_TO` = `adss_2012@yahoo.com` (optional — this is the default)

c) DNS (Cloudflare dashboard → your domain → DNS). MailChannels requires:
   - SPF record authorizing them. If you have no SPF yet, add:
     `TXT @ "v=spf1 include:relay.mailchannels.net ~all"`
     If you already have an SPF record, merge: add `include:relay.mailchannels.net` inside it (only ONE SPF record per domain).
   - DKIM is verified automatically by MailChannels once SPF authorizes the domain.

c) Redeploy after adding env vars. Test the form — you should receive a formatted HTML email at `adss_2012@yahoo.com`.

## 4. Custom domain
Pages → Custom domains → Set up a custom domain → enter your domain → Activate.
Cloudflare adds the DNS records automatically.

## 5. Before launch checklist
- [ ] Replace `base_url` in `src/build.py` (`https://rapmould.com`) with the real domain, rebuild, redeploy. (Canonical URLs + sitemap depend on it.)
- [ ] Replace photo placeholders with real workshop/team photos.
- [ ] Confirm the workshop address (currently "Bojnord, North Khorasan, Iran").
- [ ] Review the English copy with the client; fix the flagged content issues (duplicate portfolio row, "flash-free" wording).
- [ ] Submit `https://YOURDOMAIN/sitemap.xml` in Google Search Console.

## Rebuilding after edits
```bash
python3 src/build.py   # regenerates dist/ — commit & push, Pages redeploys automatically
```

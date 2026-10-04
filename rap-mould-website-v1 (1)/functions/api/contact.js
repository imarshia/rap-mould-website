/**
 * Cloudflare Pages Function — POST /api/contact
 * Receives the website contact form and emails it to adss_2012@yahoo.com
 * via MailChannels (no API key needed when sent from Workers/Pages).
 *
 * REQUIRED DNS (one-time, in the Cloudflare dashboard for your domain):
 *   1. SPF:    TXT @  "v=spf1 include:_spf.mx.cloudflare.net include:relay.mailchannels.net ~all"
 *              (merge with any existing SPF record instead of creating a second one)
 *   2. DKIM:   TXT _mailchannels.<yourdomain>  "v=mc1 cfid=<yourdomain>._domainkey.<yourdomain>"
 *              (MailChannels verifies domain ownership automatically once SPF includes them)
 *   3. Domain Lockdown: MailChannels only sends for domains that authorize it —
 *      the SPF include above is what authorizes it.
 *
 * ENV VARS (Pages > Settings > Environment variables):
 *   MAIL_FROM            — e.g. website@rapmould.com (must be on YOUR domain, not yahoo.com)
 *   MAIL_TO              — defaults to adss_2012@yahoo.com
 *   TURNSTILE_SECRET_KEY — Cloudflare Turnstile secret key (dashboard > Turnstile > your site)
 *                          The matching site key goes in src/build.py as turnstile_site_key.
 */

const MAIL_TO_DEFAULT = 'adss_2012@yahoo.com';

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function emailTemplate({ name, email, subject, message, date, source }) {
  const msgHtml = esc(message).replace(/\n/g, '<br>');
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F4F5F6;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:640px;margin:0 auto;padding:32px 16px;">
    <div style="background:#0B3D91;border-radius:12px 12px 0 0;padding:28px 32px;">
      <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px;">R.A.P MOULD</div>
      <div style="color:#BFC0C0;font-size:13px;margin-top:4px;">Rahkar Andishan Pars Ghaleb — Website Inquiry</div>
    </div>
    <div style="background:#ffffff;border:1px solid #DEDFE0;border-top:none;border-radius:0 0 12px 12px;padding:32px;">
      <h2 style="margin:0 0 20px;font-size:18px;color:#2E2E2E;">New message from the website contact form</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;color:#2E2E2E;">
        <tr><td style="padding:10px 0;border-bottom:1px solid #EDEEEF;width:140px;color:#777;font-weight:bold;">Name</td>
            <td style="padding:10px 0;border-bottom:1px solid #EDEEEF;">${esc(name)}</td></tr>
        <tr><td style="padding:10px 0;border-bottom:1px solid #EDEEEF;color:#777;font-weight:bold;">Email</td>
            <td style="padding:10px 0;border-bottom:1px solid #EDEEEF;"><a href="mailto:${esc(email)}" style="color:#0B3D91;">${esc(email)}</a></td></tr>
        <tr><td style="padding:10px 0;border-bottom:1px solid #EDEEEF;color:#777;font-weight:bold;">Subject</td>
            <td style="padding:10px 0;border-bottom:1px solid #EDEEEF;">${esc(subject) || '—'}</td></tr>
        <tr><td style="padding:10px 0;border-bottom:1px solid #EDEEEF;color:#777;font-weight:bold;">Date</td>
            <td style="padding:10px 0;border-bottom:1px solid #EDEEEF;">${esc(date)}</td></tr>
        <tr><td style="padding:10px 0;color:#777;font-weight:bold;vertical-align:top;">Message</td>
            <td style="padding:10px 0;">${msgHtml}</td></tr>
      </table>
      <div style="margin-top:24px;padding:14px 16px;background:#E8EEF9;border-radius:8px;font-size:13px;color:#0B3D91;">
        Reply directly to this email to answer <strong>${esc(name)}</strong> at <strong>${esc(email)}</strong>.
      </div>
    </div>
    <div style="text-align:center;margin-top:16px;font-size:12px;color:#999;">
      Sent automatically from the R.A.P MOULD website contact form (${esc(source)})
    </div>
  </div>
</body></html>`;
}

async function verifyTurnstile(token, secret, ip) {
  const form = new URLSearchParams();
  form.append('secret', secret);
  form.append('response', token);
  if (ip) form.append('remoteip', ip);
  const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: form,
  });
  if (!res.ok) return false;
  const out = await res.json().catch(() => ({}));
  return out.success === true;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  let data;
  try {
    data = await request.json();
  } catch {
    return Response.json({ error: 'Invalid request format.' }, { status: 400 });
  }

  // Honeypot (bots fill it; the real form never sends it with a value)
  if (data.website) {
    return Response.json({ ok: true });
  }

  const name = String(data.name || '').trim().slice(0, 120);
  const email = String(data.email || '').trim().slice(0, 160);
  const subject = String(data.subject || '').trim().slice(0, 180);
  const message = String(data.message || '').trim().slice(0, 5000);

  if (name.length < 2) return Response.json({ error: 'Please enter your name.' }, { status: 400 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email))
    return Response.json({ error: 'Please enter a valid email address.' }, { status: 400 });
  if (message.length < 10) return Response.json({ error: 'Please write your message.' }, { status: 400 });

  // Cloudflare Turnstile captcha — verified server-side, fail closed
  const captchaToken = String(data.captcha || '').trim();
  if (!env.TURNSTILE_SECRET_KEY) {
    return Response.json({ error: 'Captcha verification is not configured yet.' }, { status: 500 });
  }
  if (!captchaToken) {
    return Response.json({ error: 'Captcha verification is required.' }, { status: 400 });
  }
  const ip = request.headers.get('cf-connecting-ip') || '';
  const captchaOk = await verifyTurnstile(captchaToken, env.TURNSTILE_SECRET_KEY, ip).catch(() => false);
  if (!captchaOk) {
    return Response.json({ error: 'Captcha verification failed. Please try again.' }, { status: 400 });
  }

  const mailFrom = env.MAIL_FROM; // e.g. website@rapmould.com — MUST be set
  const mailTo = env.MAIL_TO || MAIL_TO_DEFAULT;
  if (!mailFrom) {
    return Response.json({ error: 'Email service is not configured yet.' }, { status: 500 });
  }

  const now = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
  const htmlBody = emailTemplate({ name, email, subject, message, date: now, source: new URL(request.url).hostname });

  const payload = {
    personalizations: [{ to: [{ email: mailTo, name: 'R.A.P MOULD' }] }],
    from: { email: mailFrom, name: 'R.A.P MOULD Website' },
    reply_to: { email, name },
    subject: `Website inquiry${subject ? ': ' + subject : ''} — ${name}`,
    content: [{ type: 'text/html', value: htmlBody }],
  };

  const mcRes = await fetch('https://api.mailchannels.net/tx/v1/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!mcRes.ok) {
    const detail = await mcRes.text().catch(() => '');
    console.error('MailChannels error', mcRes.status, detail.slice(0, 500));
    return Response.json({ error: 'The message could not be sent right now. Please email us directly.' }, { status: 502 });
  }

  return Response.json({ ok: true });
}

// Block other methods explicitly
export async function onRequest(context) {
  if (context.request.method === 'POST') return onRequestPost(context);
  return Response.json({ error: 'Method not allowed.' }, { status: 405 });
}

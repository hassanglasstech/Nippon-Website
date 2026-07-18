"""Nippon Hardware — quotation QR card generator.
Change URL below and re-run:  python qr/generate_qr.py
Outputs: qr/nippon-qr-card.svg (print), qr/nippon-qr-card.png (ERP paste), qr/nippon-qr-plain.png
"""
import segno, io, base64, os
from PIL import Image, ImageDraw, ImageFont

# ================= EDIT THIS =================
URL = "https://www.nipponhardware.com.pk"       # final live website URL
URL_LABEL = "www.nipponhardware.com.pk"         # shown on the card
# =============================================

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = (26, 68, 128); DARK = (22, 24, 26); GRAY = (107, 113, 119)
BORDER = (216, 216, 216)
FB = r"C:\Windows\Fonts\arialbd.ttf"; FR = r"C:\Windows\Fonts\arial.ttf"

# ---- QR (high error correction for print robustness) ----
qr = segno.make(URL, error='h')
qr.save(os.path.join(OUT, 'nippon-qr-plain.png'), scale=20, border=4, dark='#000000', light='#ffffff')
buf = io.BytesIO(); qr.save(buf, kind='png', scale=20, border=4, dark='#000000', light='#ffffff')
qr_png = buf.getvalue()
qr_b64 = base64.b64encode(qr_png).decode()

# ---- layout (base units) ----
W, H = 340, 344
QX, QY, QS = 62, 26, 216
DIV_Y = 264
LBL_Y = 290           # baseline for "SCAN FOR FULL CATALOGUE"
URL_Y = 320           # baseline for website name (big)
MAXW = W - 40

# auto-fit URL font size (<= 19) so it never overflows
_m = ImageDraw.Draw(Image.new('RGB', (10, 10)))
URL_FS = 19
while URL_FS > 13 and _m.textlength(URL_LABEL, font=ImageFont.truetype(FB, URL_FS)) > MAXW:
    URL_FS -= 1

# ================= SVG CARD (vector, print) =================
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="#ffffff" stroke="#D8D8D8"/>
  <rect x="{QX-8}" y="{QY-8}" width="{QS+16}" height="{QS+16}" rx="3" fill="#ffffff" stroke="#E8EAED"/>
  <image x="{QX}" y="{QY}" width="{QS}" height="{QS}" href="data:image/png;base64,{qr_b64}"/>
  <rect x="{W/2-24}" y="{DIV_Y}" width="48" height="3" rx="1.5" fill="#1A4480"/>
  <text x="{W/2}" y="{LBL_Y}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" letter-spacing="1.4" fill="#6B7177">SCAN FOR FULL CATALOGUE</text>
  <text x="{W/2}" y="{URL_Y}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="{URL_FS}" font-weight="700" letter-spacing="0.3" fill="#1A4480">{URL_LABEL}</text>
</svg>'''
open(os.path.join(OUT, 'nippon-qr-card.svg'), 'w', encoding='utf-8').write(svg)

# ================= PNG CARD (Pillow, ERP paste) =================
S = 5
Wp, Hp = W*S, H*S
img = Image.new('RGB', (Wp, Hp), (255, 255, 255))
d = ImageDraw.Draw(img)
d.rounded_rectangle([1, 1, Wp-2, Hp-2], radius=8*S, outline=BORDER, width=max(1, S), fill=(255, 255, 255))

def tracked_width(dr, text, fnt, track):
    return sum(dr.textlength(ch, font=fnt) for ch in text) + track*(len(text)-1)

def draw_tracked_mid(dr, y, text, fnt, fill, track):
    tw = tracked_width(dr, text, fnt, track)
    cx = (Wp - tw)/2
    for ch in text:
        dr.text((cx, y), ch, font=fnt, fill=fill)
        cx += dr.textlength(ch, font=fnt) + track

# QR panel + QR
qx, qy, qs = QX*S, QY*S, QS*S
d.rounded_rectangle([qx-8*S, qy-8*S, qx+qs+8*S, qy+qs+8*S], radius=3*S, outline=(232, 234, 237), width=max(1, S), fill=(255, 255, 255))
qimg = Image.open(io.BytesIO(qr_png)).resize((qs, qs), Image.NEAREST)
img.paste(qimg, (qx, qy))

# divider
d.rounded_rectangle([Wp/2-24*S, DIV_Y*S, Wp/2+24*S, DIV_Y*S+3*S], radius=2*S, fill=NAVY)
# label (top of text ~ baseline-ish; use top y so it sits under divider)
draw_tracked_mid(d, (LBL_Y-11)*S, "SCAN FOR FULL CATALOGUE", ImageFont.truetype(FB, 12*S), GRAY, 1.4*S)
# website name (big, navy)
f_url = ImageFont.truetype(FB, URL_FS*S)
uw = d.textlength(URL_LABEL, font=f_url)
d.text(((Wp-uw)/2, (URL_Y-URL_FS+2)*S), URL_LABEL, font=f_url, fill=NAVY)

img.save(os.path.join(OUT, 'nippon-qr-card.png'), dpi=(300, 300))
print("URL:", URL, "| url font:", URL_FS)
print("card:", img.size)

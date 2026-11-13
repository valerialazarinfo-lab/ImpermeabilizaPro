from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = "https://impermeabilizapro.pt/assinatura/"
OUT = Path("assinaturas/vinicius")
OUT.mkdir(parents=True, exist_ok=True)

def fetch(name):
    req = Request(ROOT + name, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=25) as response:
        return Image.open(BytesIO(response.read())).convert("RGBA")

def font(size, bold=False):
    name = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(name, max(8, size))

def fit_text(draw, text, max_width, start_size, bold=False):
    size = start_size
    while size > 7 and draw.textbbox((0,0), text, font=font(size,bold))[2] > max_width:
        size -= 1
    return font(size,bold)

identity = fetch("identidade.png")
w,h = identity.size
draw = ImageDraw.Draw(identity)
# The original image contains the name and job title baked into the bottom-right identity area.
# Preserve logo/company art in the top and left area.
x0 = round(w * 0.38)
y0 = round(h * 0.535)
x1 = w - 2
y1 = round(h * 0.78)
draw.rectangle((x0,y0,x1,y1), fill=(255,255,255,255))
name = "Vinícius Nascimento"
job = "Diretor Técnico e Operações"
draw.text((x0+3,y0+2),name,font=fit_text(draw,name,x1-x0-9,round(h*.084),True),fill="#081d43")
draw.text((x0+3,y0+round(h*.14)),job,font=fit_text(draw,job,x1-x0-9,round(h*.048)),fill="#354662")
identity.save(OUT/"identidade.png",optimize=True)

phone = fetch("telefone.png")
w,h=phone.size
draw=ImageDraw.Draw(phone)
# Retain the original blue icon and label; replace only the phone number.
x0=round(w*.19)
y0=round(h*.18)
draw.rectangle((x0,y0,w-2,h-1),fill=(255,255,255,255))
draw.text((x0+1,round(h*.23)), "Telefone / WhatsApp:", font=font(round(h*.13)), fill="#43526a")
number = "+351 930 446 198"
draw.text((x0+1,round(h*.53)),number,font=fit_text(draw,number,w-x0-5,round(h*.18),True),fill="#081d43")
phone.save(OUT/"telefone.png",optimize=True)
print("Generated",identity.size,phone.size)

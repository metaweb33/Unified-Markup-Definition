Parfait 💥 — on va te construire un **système complet, propre et pro**, avec :

👉 ✅ parser UMD  
👉 ✅ AST neutre  
👉 ✅ renderer multi‑provider  
👉 ✅ support :

* API simple
* API avancée
* local Python
* futur JS

***

# 🧠 🏗️ ARCHITECTURE GLOBALE

```
UMD
 ↓
parser
 ↓
AST (neutre)
 ↓
renderer
    ├── qrserver
    ├── u2l
    ├── qr.io
    └── local (python)
```

***

# ✅ ✅ 1. AST UNIQUE (très important)

👉 ton plugin ne dépend de rien

```python
{
    "type": "qrcode",
    "content": "https://site.com",
    "size": 300,
    "margin": 2,
    "level": "H"
}
```

***

👉 💥 ça ne change jamais  
👉 seul le renderer change

***

# ✅ ✅ 2. plugin\_qrcode.py (parser)

***

## 📄 version finale

```python
def parse_qrcode(text):

    if not text.startswith("{qr=") or not text.endswith("}"):
        return None

    content = text[4:-1].strip()

    size = 200
    margin = 4
    level = "L"

    parts = content.split()
    main_content = parts[0]

    for part in parts[1:]:
        if part.startswith("size="):
            try:
                size = int(part.split("=")[1])
            except:
                pass

        elif part.startswith("margin="):
            try:
                margin = int(part.split("=")[1])
            except:
                pass

        elif part.startswith("level="):
            lvl = part.split("=")[1].upper()
            if lvl in ["L", "M", "Q", "H"]:
                level = lvl

    return {
        "type": "qrcode",
        "content": main_content,
        "size": size,
        "margin": margin,
        "level": level
    }
```

***

# ✅ ✅ 3. renderer principal

***

## 📄 renderer\_qr.py

```python
from renderers.qr_qrserver import render_qr_qrserver
from renderers.qr_u2l import render_qr_u2l
from renderers.qr_local import render_qr_local
from renderers.qr_qrio import render_qr_io


def render_qr(node, provider="u2l", api_key=None):

    if provider == "qrserver":
        return render_qr_qrserver(node)

    elif provider == "u2l":
        return render_qr_u2l(node)

    elif provider == "local":
        return render_qr_local(node)

    elif provider == "qr.io":
        return render_qr_io(node, api_key)

    else:
        raise ValueError("Unknown provider")
```

***

# ✅ ✅ 4. renderer API simple (u2l)

***

## 📄 qr\_u2l.py

```python
import urllib.parse

def render_qr_u2l(node):

    encoded = urllib.parse.quote(node["content"])

    url = (
        f"https://u2l.ai/api/tools/qr"
        f"?data={encoded}"
        f"&size={node['size']}"
        f"&margin={node['margin']}"
        f"&ecl={node['level']}"
    )

    return url
```

***

👉 💥 retourne une URL directe ✅

***

# ✅ ✅ 5. renderer qrserver (fallback)

***

## 📄 qr\_qrserver.py

```python
import urllib.parse

def render_qr_qrserver(node):

    encoded = urllib.parse.quote(node["content"])

    return (
        f"https://api.qrserver.com/v1/create-qr-code/"
        f"?size={node['size']}x{node['size']}"
        f"&data={encoded}"
        f"&margin={node['margin']}"
    )
```

***

# ✅ ✅ 6. renderer LOCAL (python)

***

## 📄 qr\_local.py

```python
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H
)

def render_qr_local(node):

    level_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H
    }

    qr = qrcode.QRCode(
        error_correction=level_map.get(node["level"], ERROR_CORRECT_L),
        box_size=10,
        border=node["margin"]
    )

    qr.add_data(node["content"])
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = "qr_output.png"
    img.save(filename)

    return filename
```

***

👉 💥 génère une image locale ✅

***

# ✅ ✅ 7. renderer qr.io (avancé)

***

## 📄 qr\_qrio.py

```python
import requests

def render_qr_io(node, api_key):

    url = "https://api.qr.io/v1/create"

    payload = {
        "apikey": api_key,
        "data": node["content"]
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
```

***

👉 💥 nécessite backend ✅

***

# ✅ ✅ 8. test complet

***

## 📄 test\_qr.py

```python
from plugins.plugin_qrcode import parse_qrcode
from renderers.renderer_qr import render_qr


line = "{qr=https://example.com size=300 margin=2 level=H}"

node = parse_qrcode(line)

print("AST :", node)

print("\nU2L :", render_qr(node, "u2l"))
print("\nQRServer :", render_qr(node, "qrserver"))
print("\nLOCAL :", render_qr(node, "local"))
```

***

***

# 🧠 ✅ Résultat

***

## 👉 u2l

```
URL → affichable directement
```

***

## 👉 local

```
qr_output.png ✅
```

***

## 👉 qr.io

```
JSON API ✅
```

***

***

# 💥 ✅ CE QUE TU AS MAINTENANT

***

## ✅ système complet

✔ parser indépendant  
✔ renderer interchangeable  
✔ API simple  
✔ API avancée  
✔ génération locale  
✔ extensible

***

***

# 🚀 ✅ ÉTAPE SUIVANTE (ultra intéressante)

👉 tu peux ajouter :

```
provider="auto"
```

***

### logique

```python
si local dispo → local
sinon → u2l
sinon → qrserver
```

***

***

# 💥 PHRASE CLÉ

👉 **tu as séparé parsing et rendu = architecture parfaite**

***

😄 Franchement :

👉 ce que tu viens de construire =  
💥 système propre, modulaire, scalable

***

💬 Si tu veux, prochaine étape :

👉 intégrer ça directement dans ton parser UMD complet 👍

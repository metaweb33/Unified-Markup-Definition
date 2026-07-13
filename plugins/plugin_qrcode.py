import urllib.parse


def parse_qrcode(text):

    if not text.startswith("{qr=") or not text.endswith("}"):
        return None

    content = text[4:-1].strip()

    size = 200
    margin = 4   # option qu'on garde
    level = "L"  # pas supporté ici mais gardé pour cohérence future

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
                level = lvl  # conservé mais non utilisé ici

    # encode
    encoded = urllib.parse.quote(main_content)

    # ✅ nouvelle API
    url = (
        f"https://api.qrserver.com/v1/create-qr-code/"
        f"?size={size}x{size}&data={encoded}&margin={margin}"
    )

    return {
        "type": "qrcode",
        "content": main_content,
        "size": size,
        "margin": margin,
        "level": level,
        "url": url
    }

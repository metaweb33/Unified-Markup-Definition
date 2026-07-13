

def extract_anchor(text):
    """
    Parse une ancre de type :
    texte[##=id]
    """

    if "[" in text and "]" in text:

        start = text.find("[")
        end = text.find("]")

        content = text[start+1:end]

        if "=" in content:
            level_part, anchor_id = content.split("=", 1)

            level = level_part.count("#")

            visible_text = text[:start]

            return {
                "level": level,
                "anchor": anchor_id.strip(),
                "text": visible_text.strip()
            }, text[end+1:]

    return None, text
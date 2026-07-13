

def extract_toc_item(text):
    """
    Parse syntax:
    label[##=id]
    """

    if "[" in text and "]" in text:

        start = text.find("[")
        end = text.find("]")

        content = text[start+1:end]

        if "=" in content:
            level_part, id_value = content.split("=", 1)

            level = level_part.count("#")

            label = text[:start].strip()

            return {
                "type": "toc_item",
                "level": level,
                "id": id_value.strip(),
                "label": label
            }, text[end+1:]

    return None, text

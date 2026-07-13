# Plugin de parsing emoji
# Emoji parser plugin

def extract_emoji(text):

    print("INPUT :", repr(text))

    if text.startswith(":") and ":" in text[1:]:
        end = text.find(":", 1)
        name = text[1:end]

        return name, text[end+1:]

        print("OUTPUT :", repr(new_text))
    return None, text

# Plugin de gestion des icones dev
# Devicon parser plugin

def extract_icon(text):

    if text.startswith("{icon=") and "}" in text:

        end = text.find("}")
        name = text[6:end]

        return {
            "icon": name
        }, text[end+1:]

    return {}, text
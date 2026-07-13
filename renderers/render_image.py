

def render_image(image):

    if not image:
        return ""

    return f'<img src="{image["src"]}" />'



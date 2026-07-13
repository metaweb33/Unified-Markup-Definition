

def render_toc(items):

    html = "<ul>"

    for item in items:
        html += f'<li><a href="#{item["id"]}">{item["label"]}</a></li>'

    html += "</ul>"

    return html
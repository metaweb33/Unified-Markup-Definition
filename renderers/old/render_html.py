from renderers.devicon_map import LANG_ALIAS

def render_document(doc):
    html_parts = []
    for node in doc.get("children", []):
        result = render_node(node)
        if result is None:
            html_parts.append("")
        else:
            html_parts.append(result)
    return "".join(html_parts)

def render_image(node):
    src = node.get("src", "")
    alt = node.get("alt", "")
    width = node.get("width", "auto")
    height = node.get("height", "auto")
    return f'<img src="{src}" alt="{alt}" width="{width}" height="{height}" style="display: inline-block; vertical-align: middle;" />'

def render_node(node):
    if not node or "type" not in node:
        return ""

    if node["type"] == "empty":
        return "<br/>"
        
    elif node["type"] == "image":
        return render_image(node)
        
    elif node["type"] == "multi_line_block":
        tag = f"h{node['level']}" if node.get("level") else "div"
        styles_css = []
        if node.get("align"):
            styles_css.append(f"text-align: {node['align']};")
        if node.get("params") and "color" in node["params"]:
            styles_css.append(f"color: {node['params']['color']};")
            
        classes = " ".join(node.get("styles", []))
        style_attr = f' style="{" ".join(styles_css)}"' if styles_css else ""
        class_attr = f' class="{classes}"' if classes else ""
        
        html_lines = []
        for inline_node in node["lines"]:
            line_html = render_inline(inline_node)
            html_lines.append(line_html if line_html is not None else "")
            
        content_html = "<br/>".join(html_lines)
        return f"<{tag}{class_attr}{style_attr}>{content_html}</{tag}>"

    elif node["type"] == "block":
        tag = f"h{node['level']}" if node.get("level") else "p"
        return f"<{tag}>{node.get('content', '')}</{tag}>"

    elif node["type"] == "separator":
        kind = node.get("kind")
        if kind == "line":
            return "<hr style='border: none; border-top: 1px solid #ccc; margin: 1em 0;'/>"
        elif kind == "dotted":
            return "<hr style='border: none; border-top: 1px dotted #888; margin: 1em 0;'/>"
        elif kind == "double":
            return "<hr style='border: none; border-top: 3px double #888; margin: 1em 0;'/>"
        elif kind == "dashed":
            return "<hr style='border: none; border-top: 1px dashed #888; margin: 1em 0;'/>"
        elif kind == "repeat":
            pattern = node.get("pattern", "")
            return f"""
            <div style="overflow: hidden; white-space: nowrap; user-select: none; margin: 1em 0; color: #666; font-family: monospace;">
                {"".join([pattern] * 150)}
            </div>
            """
        return "<hr/>"

    elif node["type"] == "code":
        lang_raw = node.get("language", "text").strip().lower()
        lang_mapping = {
            "python": "python", "c++": "cplusplus", "cpp": "cplusplus",
            "c#": "csharp", "csharp": "csharp", "javascript": "javascript",
            "js": "javascript", "typescript": "typescript", "ts": "typescript",
            "html": "html5", "css": "css3", "java": "java", "php": "php",
            "ruby": "ruby", "go": "go", "rust": "rust"
        }
        lang_id = lang_mapping.get(lang_raw, lang_raw)
        display_name = lang_raw.upper() if lang_raw != "cpp" else "C++"
        
        icon_html = ""
        if lang_id != "text":
            icon_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{lang_id}/{lang_id}-original.svg"
            icon_html = f'<img src="{icon_url}" width="20" height="20" alt="" style="margin-right: 8px; display: inline-block; vertical-align: middle;"/>'
        
        escaped_code = node.get('content', '').replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines = escaped_code.split('\n')
        formatted_lines = []
        for line in lines:
            line_content = line if line != "" else "&nbsp;"
            formatted_lines.append(f'<span class="code-line">{line_content}</span>')
        
        gutter_and_code = "".join(formatted_lines)

        return (
            f'<div class="code-block-container" style="margin: 1.5em 0; border: 1px solid #ccc; border-radius: 6px; overflow: hidden; font-family: sans-serif; background-color: #ffffff; width: 100%; box-sizing: border-box; white-space: normal;">'
            f'<div class="code-block-header" style="background-color: #f6f8fa; padding: 6px 12px; border-bottom: 1px solid #ccc; display: flex; align-items: center; font-size: 0.85em; color: #444; font-weight: bold;">'
            f'{icon_html}<span style="display: inline-block; vertical-align: middle;">{display_name}</span>'
            f'</div>'
            f'<pre class="code-container"><code>{gutter_and_code}</code></pre>'
            f'</div>'
        )

    elif node["type"] == "inline":
        return render_inline(node)

    return ""

def render_block(node):
    level = node.get("level", 1)
    content = node.get("content", "")
    styles = node.get("styles", [])
    params = node.get("params", {})
    align = node.get("align")

    tag = f"h{level}" if node.get("structure") == "heading" else "div"
    style_str = build_style(styles, params, align)

    return f'<{tag} style="{style_str}">{content}</{tag}>'

def render_inline(node):
    segments = node.get("segments", [])
    html_parts = []
    for seg in segments:
        if seg.get("type") == "break":
            html_parts.append("<br/>")
            continue
        html_parts.append(render_segment(seg))
    return f'<div>{"".join(html_parts)}</div>'

def render_code_inline(seg):
    # Support de 'content' ou 'text' pour s'adapter fidèlement à ton AST
    content = seg.get("content", seg.get("text", ""))
    escaped_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<code class="inline-code">{escaped_content}</code>'

def render_segment(seg):
    t = seg.get("type")

    if t == "text":
        return seg.get("text", "")

    elif t == "styled":
        style_str = build_style(seg.get("styles", []), seg.get("params", {}), None)
        return f'<span style="{style_str}">{seg.get("text", "")}</span>'

    elif t == "code_inline":
        return render_code_inline(seg)

    elif t == "image":
        return render_image(seg)

    elif t == "emoji":
        return seg.get("value", "")

    elif t == "icon":
        return f"[{seg.get('name')}]"

    return ""

def render_empty(node):
    return '<div class="umd-space"></div>'

def render_separator(node):
    kind = node.get("kind", "line")
    if kind == "line":
        return "<hr>"
    if kind == "double":
        return '<hr class="sep-double">'
    if kind == "dotted":
        return '<hr class="sep-dotted">'
    if kind == "wave":
        return '<hr class="sep-wave">'
    if kind == "dashed":
        return '<hr class="sep-dashed">'
    if kind == "repeat":
        pattern = node.get("pattern", "-")
        line = ""
        while len(line) < 80:
            line += pattern
        return f'<div class="sep-repeat">{line[:80]}</div>'
    return "<hr>"

def render_toc_item(node):
    label = node.get("label", "")
    id_ = node.get("id", "")
    return f'{id_}">{label}</a>'

def build_style(styles, params, align):
    css = []

    if "bold" in styles:
        css.append("font-weight:bold")
    if "italic" in styles:
        css.append("font-style:italic")

    decorations = []
    if "underline" in styles:
         decorations.append("underline")
    if "strike" in styles:
        decorations.append("line-through")
    if decorations:
        css.append(f"text-decoration:{' '.join(decorations)}")

    if "underline_double" in styles:
        css.append("text-decoration-line:underline")
        css.append("text-decoration-style:double")
    if "underline_dot" in styles:
        css.append("text-decoration-line:underline")
        css.append("text-decoration-style:dotted")
    if "underline_wavy" in styles:
        css.append("text-decoration-line:underline")
        css.append("text-decoration-style:wavy")
    if "underline_dashdot" in styles:
        css.append("text-decoration-line:underline")
        css.append("text-decoration-style:dashed")
    if "underline_bold" in styles:
        css.append("text-decoration-line:underline")
        css.append("text-decoration-thickness:4px")

    if "highlight" in styles:
        css.append("background:yellow")

    if "color" in params:
        css.append(f"color:{params['color']}")
    if "size" in params:
        css.append(f"font-size:{params['size']}px")
    if "font" in params:
        css.append(f"font-family:{params['font']}")

    if align == "center":
        css.append("text-align:center")
    elif align == "right":
        css.append("text-align:right")
    elif align == "left":
        css.append("text-align:left")

    return "; ".join(css)
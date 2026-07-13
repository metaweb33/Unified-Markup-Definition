from renderers.devicon_map import LANG_ALIAS


def render_document(doc):
    """Génère la page HTML finale pour le QWebEngineView."""
    body_html = []
    children = doc.get("children", []) if isinstance(doc, dict) else doc

    for child in children:
        body_html.append(render_node(child))

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
            padding: 20px;
            background-color: #fff;
        }}
        .umd-paragraph {{
            margin-bottom: 1em;
            white-space: pre-wrap;
        }}
        .inline-code {{
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }}
        h1, h2, h3 {{ color: #111; margin-top: 1.5em; margin-bottom: 0.5em; }}
        
        .code-block-container {{
            margin: 1.5em 0;
            border: 1px solid #ccc;
            border-radius: 6px;
            overflow: hidden;
            font-family: sans-serif;
            background-color: #ffffff;
            width: 100%;
            box-sizing: border-box;
            white-space: normal;
        }}
        .code-block-header {{
            background-color: #f6f8fa;
            padding: 6px 12px;
            border-bottom: 1px solid #ccc;
            display: flex;
            align-items: center;
            font-size: 0.85em;
            color: #444;
            font-weight: bold;
        }}
        .code-container {{
            margin: 0;
            padding: 12px 0;
            background: #fafafa;
            border: none;
            white-space: pre-wrap;    
            word-break: break-all;
            tab-size: 4;
        }}
        .code-line {{
            display: block;
            padding-left: 12px;
            padding-right: 12px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #333;
        }}
    </style>
</head>
<body>
{"\n".join(body_html)}
</body>
</html>"""
    return full_html


def render_node(node):
    if not node or "type" not in node:
        return ""

    node_type = node["type"]

    if node_type == "empty":
        return "<br/>"
    elif node_type == "image":
        return render_image(node)
    elif node_type == "multi_line_block":
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
    elif node_type == "block":
        tag = f"h{node['level']}" if node.get("level") else "p"
        return f"<{tag}>{node.get('content', '')}</{tag}>"
    elif node_type == "separator":
        return render_separator_node(node)
    elif node_type == "code":
        return render_code_node(node)
    elif node_type == "inline":
        return render_inline(node)

    return ""


def render_image(node):
    src = node.get("src", "")
    alt = node.get("alt", "")
    width = node.get("width", "auto")
    height = node.get("height", "auto")
    return f'<img src="{src}" alt="{alt}" width="{width}" height="{height}" style="display: inline-block; vertical-align: middle;" />'


def render_separator_node(node):
    kind = node.get("kind")
    color = node.get("params", {}).get("color")

    if kind == "line":
        c = color or "#ccc"
        return f"<hr style='border: none; border-top: 1px solid {c}; margin: 1em 0;'/>"
    elif kind == "dotted":
        c = color or "#888"
        return f"<hr style='border: none; border-top: 1px dotted {c}; margin: 1em 0;'/>"
    elif kind == "double":
        c = color or "#888"
        return f"<hr style='border: none; border-top: 3px double {c}; margin: 1em 0;'/>"
    elif kind == "dashed":
        c = color or "#888"
        return f"<hr style='border: none; border-top: 1px dashed {c}; margin: 1em 0;'/>"
    elif kind == "repeat":
        pattern_data = node.get("pattern", "")
        if isinstance(pattern_data, list):
            html_chunks = []
            for token in pattern_data:
                char = token.get("char", "")
                c = token.get("color") or color or "#666"
                html_chunks.append(f"<span style='color: {c};'>{char}</span>")
            html_pattern = "".join(html_chunks)
            motif_len = sum(len(t.get("char", "")) for t in pattern_data) or 1
        else:
            c = color or "#666"
            html_pattern = f"<span style='color: {c};'>{pattern_data}</span>"
            motif_len = len(pattern_data) or 1

        nb_reps = max(1, 120 // motif_len)
        return f"""<div style="overflow: hidden; white-space: nowrap; user-select: none; margin: 1em 0; font-family: monospace; font-size: 14px;">{"".join([html_pattern] * nb_reps)}</div>"""

    if color:
        return f"<hr style='border: none; border-top: 1px solid {color}; margin: 1em 0;'/>"
    return "<hr/>"


def render_code_node(node):
    lang_raw = node.get("language", "text").strip().lower()
    lang_mapping = {
        "python": "python",
        "c++": "cplusplus",
        "cpp": "cplusplus",
        "c#": "csharp",
        "csharp": "csharp",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "html": "html5",
        "css": "css3",
        "java": "java",
        "php": "php",
        "ruby": "ruby",
        "go": "go",
        "rust": "rust",
    }
    lang_id = lang_mapping.get(lang_raw, lang_raw)
    display_name = lang_raw.upper() if lang_raw != "cpp" else "C++"

    icon_html = ""
    if lang_id != "text":
        icon_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{lang_id}/{lang_id}-original.svg"
        icon_html = f'<img src="{icon_url}" width="20" height="20" alt="" style="margin-right: 8px; display: inline-block; vertical-align: middle;"/>'

    escaped_code = (
        node.get("content", "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    lines = escaped_code.split("\n")
    formatted_lines = []
    for line in lines:
        line_content = line if line != "" else "&nbsp;"
        formatted_lines.append(f'<span class="code-line">{line_content}</span>')

    gutter_and_code = "".join(formatted_lines)

    return (
        f'<div class="code-block-container">'
        f'<div class="code-block-header">'
        f'{icon_html}<span style="display: inline-block; vertical-align: middle;">{display_name}</span>'
        f'</div>'
        f'<pre class="code-container"><code>{gutter_and_code}</code></pre>'
        f'</div>'
    )


def render_inline(node):
    segments = node.get("segments", [])
    html_parts = []
    for seg in segments:
        seg_type = seg.get("type")
        
        # 1. Gestion du saut de ligne
        if seg_type == "break":
            html_parts.append("<br/>")
            continue
            
        # 2. Gestion des images inline
        elif seg_type == "image":
            html_parts.append(render_image(seg))
            continue
            
        # 3. Sécurité pour les Emojis (pour éviter qu'ils soient vidés)
        elif seg_type == "emoji":
            html_parts.append(seg.get("value", ""))
            continue
            
        # 4. Sécurité pour les Icônes
        elif seg_type == "icon":
            html_parts.append(f"<i>{seg.get('name', '')}</i>")
            continue
            
        # 5. Appel de ton VRAI renderer de segment
        html_parts.append(render_segment_to_html(seg)) 
        
    return f'<div>{"".join(html_parts)}</div>'

def build_style(styles, params=None, align=None):
    """Construit les attributs CSS de manière atomique pour éviter les conflits."""
    if params is None:
        params = {}
    css = []

    if "bold" in styles:
        css.append("font-weight: bold;")
    if "italic" in styles:
        css.append("font-style: italic;")

    # Accumulation propre des décorations de texte pour éviter d'écraser la rature
    decorations = []
    has_underline_style = any(s.startswith("underline") for s in styles)

    if "underline" in styles or has_underline_style:
        decorations.append("underline")
    if "strike" in styles:
        decorations.append("line-through")

    if decorations:
        css.append(f"text-decoration-line: {' '.join(decorations)};")

    # Application des modificateurs de style uniquement
    if "underline_double" in styles:
        css.append("text-decoration-style: double;")
    if "underline_dot" in styles:
        css.append("text-decoration-style: dotted;")
    if "underline_wavy" in styles:
        css.append("text-decoration-style: wavy;")
    if "underline_dashdot" in styles:
        css.append("text-decoration-style: dashed;")
    if "underline_bold" in styles:
        css.append("text-decoration-thickness: 4px;")

    # Détection et rendu sécurisé du Highlight (Couleur personnalisée ou jaune par défaut)
    for s in styles:
        if s == "highlight":
            h_color = (
                params.get("highlight_color")
                or params.get("highlight")
                or "yellow"
            )
            css.append(f"background-color: {h_color};")
            break
        elif s.startswith("highlight_"):
            h_color = s.split("_")[1]
            css.append(f"background-color: {h_color};")
            break

    if "color" in params:
        css.append(f"color: {params['color']};")
    if "size" in params:
        css.append(f"font-size: {params['size']}px;")
    if "font" in params:
        css.append(f"font-family: {params['font']};")

    if align == "center":
        css.append("text-align: center;")
    elif align == "right":
        css.append("text-align: right;")
    elif align == "left":
        css.append("text-align: left;")

    return " ".join(css)


def render_segment_to_html(node):
    """Détermine s'il faut séparer le rendu en cas de conflits de couleurs de

    traits.
    """
    if node.get("type") in ("code_inline", "inline_code"):
        content = node.get("content", node.get("text", ""))
        escaped = (
            content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f'<code class="inline-code">{escaped}</code>'

    styles = node.get("styles", [])
    params = node.get("params", {})
    text = node.get("text", "")

    has_underline_style = any(s.startswith("underline") for s in styles)

    # PROTECTION ANTI-FUITE : Récupère la couleur uniquement si le style associé est actif
    u_color = params.get("underline_color") if has_underline_style else None
    s_color = params.get("strike_color") if "strike" in styles else None

    # Si le souligné et le barré cohabitent et possèdent des couleurs distinctes
    if (
        has_underline_style
        and "strike" in styles
        and u_color
        and s_color
        and u_color != s_color
    ):
        styles_sans_strike = [s for s in styles if s != "strike"]
        css_outer = build_style(styles_sans_strike, params)
        if u_color:
            css_outer += f" text-decoration-color: {u_color};"

        params_inner = {"strike_color": s_color}
        if "color" in params:
            params_inner["color"] = params["color"]
        css_inner = build_style(["strike"], params_inner)
        if s_color:
            css_inner += f" text-decoration-color: {s_color};"

        return f'<span style="{css_outer}"><span style="{css_inner}">{text}</span></span>'

    else:
        css_string = build_style(styles, params)
        if has_underline_style and u_color:
            css_string += f" text-decoration-color: {u_color};"
        if "strike" in styles and s_color:
            css_string += f" text-decoration-color: {s_color};"
        return f'<span style="{css_string}">{text}</span>'
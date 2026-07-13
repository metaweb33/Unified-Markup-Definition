from parser import parse_line
from plugins.plugin_code import parse_code
from renderers.render_html import render


def parse_document(lines):

    result = []
    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # ---- CODE BLOCK ----
        if line.startswith("```"):
            node, i = parse_code(lines, i)
            result.append(node)
            continue

        # ---- NORMAL LINE ----
        node = parse_line(line)
        result.append(node)

        i += 1

    return result


# ---- TEST ----
with open("test.umd", "r", encoding="utf-8") as f:
    lines = f.readlines()

nodes = parse_document(lines)
print(nodes)

html_output = [render(node) for node in nodes]

# ---- HTML FILE ----
html_full = f"""
<html>
<head>
<meta charset="utf-8">
<title>UMD Testtitle>
</head>
<body>

{"".join(html_output)}

</body>
</html>
"""

with open("output.html", "w", encoding="utf-8") as f:
    f.write(html_full)

print("✅ output.html généré")
#!/usr/bin/env python3
import sys


values = sys.stdin.read().rstrip("\n")
if not values:
    sys.exit(0)

fields = values.split("|", 11)
if len(fields) != 12:
    print(f"Expected 12 form values, received {len(fields)}", file=sys.stderr)
    sys.exit(1)

(
    comment,
    exp_indice,
    style,
    text_color,
    highlight,
    highlight_color,
    underline,
    underline_color,
    strike,
    strike_color,
    content,
    closing
) = fields

styles = {
    "aucun": "",
    "gras": "**",
    "italique": "*",
    "gras+italique": "***",
}
underlines = {
    "aucun": "",
    "simple": "_",
    "double": "__",
    "epais": "___",
    "points": "_._",
    "tirets": "_-_",
    "double-tirets": "_=_",
    "ondule": "_~_",
    "scie": "_^_",
    "point-trait": "_!_",
}
Closing = {
    "aucun": "",
    "tout" : "{/}",
    "gras": "/**",
    "italique": "/*",
    "gras+italique": "/***",
    "couleurs" : "/&",
    "text-color" : "&&",
    "highlight-color" : "&==",
    "underline-color" : "&_",
    "strike-color" : "&~~",
    "underline" : "/_",
    "comment" : "/\`",

}


def color(value):
    return "" if value == "heritée" else "{" + value + "}"


opening = ""

if exp_indice == "exposant":
    opening += "^"
    exp_indice_closing = "/^"
elif exp_indice == "indice":
    opening += "~"
    exp_indice_closing = "/~"
else:
    exp_indice_closing = ""

if highlight == "oui":
    opening += color(highlight_color) + "=="

underline_marker = underlines.get(underline, "")
if underline_marker:
    opening += color(underline_color) + underline_marker

if strike == "oui":
    opening += color(strike_color) + "~~"

opening += color(text_color)
opening += styles.get(style, "")

if comment == "oui":
    opening = "`" + opening

closing = exp_indice_closing + Closing.get(closing, closing)

print(f"{opening}{content}{closing}")

# Plugin de parsing des styles
# Style parser plugin

# IMPORTANT : ordre du plus long au plus court
STYLE_TOKENS = [

    # bold + italic
    ("***", ["bold", "italic"]),
    ("**", ["bold"]),
    ("*", ["italic"]),

    # décorations
    ("~~", ["strike"]),
    ("==", ["highlight"]),

    # underline variants (longest first)
    ("___", ["underline_bold"]),

    ("__:", ["underline_dot"]),
    ("__~", ["underline_wavy"]),
    ("__!", ["underline_dashdot"]),
    
    ("__", ["underline_double"]),
    ("_", ["underline"]),
]


def extract_styles(text):
    """
    FR: Extrait les styles au début du texte
    EN: Extract styles from the beginning of the text

    Returns:
        (styles, remaining_text)
    """

    #print("INPUT :", repr(text))

    styles = []
    i = 0

    while i < len(text):

        matched = False

        for token, style_list in STYLE_TOKENS:

            if text.startswith(token, i):
                styles.extend(style_list)
                i += len(token)
                matched = True
                break

        if not matched:
            break

    #print("OUTPUT :", styles)

    return styles, text[i:]

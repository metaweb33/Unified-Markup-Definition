from renderers.devicon_map import LANG_ALIAS


def render_code(node):

    lang = node.get("language", "").lower()
    content = node.get("content", "")

    icon_lang = LANG_ALIAS.get(
        lang,
        lang
    )

    icon_file = f"{icon_lang}-original.svg"

    icon_html = f"""
    <img
    src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{icon_lang}/{icon_file}"
    class="code-icon"
    />
    """

    label_html = (
        f'<span class="code-lang">{lang}</span>'
    )

    # ---- LINE NUMBER ----

    lines = content.split("\n")

    numbers = "<br>".join(
        str(i)
        for i in range(1, len(lines) + 1)
    )
    print("GUTTER =", numbers)
    
    # ---- HTML ----

    return f"""
    <div class="code-block">

        <div class="code-header">
            {icon_html}
            {label_html}
        </div>

        <div style="background:red;color:white">
            TEST GUTTER
        </div>


        <div class="code-body">

            <div class="code-gutter">
                {numbers}
            </div>

            <pre><code class="language-{lang}">
        {content}
            </code></pre>

        </div>

    </div>
    """
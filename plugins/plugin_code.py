# Plugin de gestion des blocs de code
# Code block parser plugin


def parse_code(lines, index):
    """
    FR: Parse un bloc de code multi-ligne.

    EN: Parse a multi-line code block.

    Args:
        lines: liste complète des lignes du document
        index: position de départ du bloc

    Returns:
        (node, new_index)
    """

    line = lines[index].strip()

    # Vérification
    if not line.startswith("```"):
        return None, index + 1

    # Langage éventuel
    language = line[3:].strip().lower()

    code_lines = []
    index += 1

    # Lecture du contenu
    while index < len(lines):

        current = lines[index]

        # Fin de bloc
        if current.strip().startswith("```"):
            index += 1
            break

        code_lines.append(current)
        index += 1

    # Construction du nœud AST
    node = {
        "type": "code",
        "language": language,
        "content": "\n".join(code_lines).rstrip()
    }

    return node, index
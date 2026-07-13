from parser import parse_line
import json   # ✅ à mettre ici, en haut

# ---- TESTS ----
lines = [
    "### Titre simple",
    "~###_**><{color=red} Titre stylé",
    "chap01[#=intro]",
    "Texte normal {color=blue}**Hello**",
    "![img:https://site.com/img.png]",
]

# ---- EXECUTION ----
for line in lines:
    result = parse_line(line)

    print("\n-----")
    print("INPUT :", line)

    # affichage lisible
    print("OUTPUT :")
    print(json.dumps(result, indent=2, ensure_ascii=False))
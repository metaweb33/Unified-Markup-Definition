from core.document_parser import parse_document
from renderers.render_html import render_document

import sys
import json

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QPlainTextEdit,
    QDockWidget  # <- Ajouté pour les volets mobiles
)

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


# --- TON COMPOSANT DE SAISIE RESTE ICI ET NE BOUGE PAS ---
class UmdEditor(QTextEdit):

    PAIRS = {
        "{": "}",
        "[": "]",
        "(": ")",
        '"': '"'
    }

    def keyPressEvent(self, event):

        # ----- cas spécial triple backtick -----
        if event.text() == "`":

            cursor = self.textCursor()

            before = self.toPlainText()[:cursor.position()]

            if before.endswith("``"):

                cursor.insertText("`\n```")

                cursor.movePosition(cursor.MoveOperation.Up)

                self.setTextCursor(cursor)

                return

        # ----- paires normales -----
        char = event.text()

        if char in self.PAIRS:

            cursor = self.textCursor()

            cursor.insertText(
                char + self.PAIRS[char]
            )

            cursor.movePosition(
                cursor.MoveOperation.Left
            )

            self.setTextCursor(cursor)
            
            return
        
        if event.key() == Qt.Key_Tab:

            cursor = self.textCursor()

            cursor.insertText("    ")

            return

        super().keyPressEvent(event)

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class UMDHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # --- 1. FORMATS DES STYLES (Couleurs et polices) ---
        
        # Bloc multi-lignes (&&)
        format_block = QTextCharFormat()
        format_block.setForeground(QColor("#2aa198"))  # Cyan discret
        format_block.setFontWeight(QFont.Bold)
        
        # Balise de Reset {}
        format_reset = QTextCharFormat()
        format_reset.setForeground(QColor("#dc322f"))  # Rouge vif pour bien voir la coupure
        format_reset.setFontWeight(QFont.Bold)
        
        # Paramètres de couleur (ex: {blue}, {red})
        format_params = QTextCharFormat()
        format_params.setForeground(QColor("#b58900"))  # Jaune/Orange doré
        
        # Gras (**)
        format_bold = QTextCharFormat()
        format_bold.setFontWeight(QFont.Bold)
        format_bold.setForeground(QColor("#cb4b16"))
        
        # Italique (*)
        format_italic = QTextCharFormat()
        format_italic.setFontItalic(True)

        # --- 2. DÉFINITION DES REGEX (L'ordre importe !) ---
        
        # Détection du bloc && en début de ligne
        self.rules.append((QRegularExpression(r"^&&.*"), format_block))
        
        # Détection de la balise de reset vide {}
        self.rules.append((QRegularExpression(r"\{\}"), format_reset))
        
        # Détection des balises de paramètres comme {blue} ou {red}
        self.rules.append((QRegularExpression(r"\{[a-zA-Z0-9_]+\}"), format_params))
        
        # Styles inline basiques (Gras et Italique)
        self.rules.append((QRegularExpression(r"\*\*[^*]+\*\*"), format_bold))
        self.rules.append((QRegularExpression(r"\*[^*]+\*"), format_italic))

    def highlightBlock(self, text):
        for expression, char_format in self.rules:
            # CORRECTION : On utilise globalMatch à la place de findIter
            match_iterator = expression.globalMatch(text)
            
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, char_format)
# --- LA MAINWINDOW ADOPTE LE LOOK "PROSELIBRE" ---
class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("UMD Studio - Mode ProseLibre")
        self.resize(1600, 900)

        # 1. ZONE CENTRALE (Éditeur + Preview)
        # On utilise un splitter horizontal au centre uniquement pour la zone de travail de l'auteur
        center_splitter = QSplitter(Qt.Horizontal)

        # Ton éditeur personnalisé d'après ta classe du dessus
        self.editor = UmdEditor()

        self.highlighter = UMDHighlighter(self.editor.document())

        self.editor.setPlainText(
            """### Introduction
Texte simple,
test sur deux lignes.
Test pour verification du retour à la ligne, si ce texte ne se retourne pas en arrivant au bout de la ligne ce serait domage.

&&### Introduction
Texte simple,
test sur deux lignes.
Test pour verification du retour à la ligne, si ce texte ne se retourne pas en arrivant au bout de la ligne ce serait domage.

&&###><{blue}
Ligne  non stylée du bloc h3 centré
{red}~~{black}_Ligne de bloc bleu centré  soulignée en noir et barré en rouge{&} mot après arrêt
{red}___{black}***Ligne bloc gras soulignée gras
&&

**bold *italique {red}~~_rouge barré souligné{&}  ***bold italic{/} normal

++
++{blue}
++{purple}
++{red}
++#{red}#{blue}#{purple}#{black}#
++!\/{red}

![Python](https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg){20x20} Imge simple avec *texte à ***droite.

Fenêtre de code :
```python
print("test")
    z += 2
    y -=1
![Python](https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg){20x20} Imge simple avec *texte à ***droite.
```

test sortie
"""
        )

        self.preview = QWebEngineView()

        center_splitter.addWidget(self.editor)
        center_splitter.addWidget(self.preview)
        center_splitter.setSizes([600, 600])

        # On fixe la zone de texte + preview au centre de l'application
        self.setCentralWidget(center_splitter)


        # 2. VOLET MOBILE GAUCHE : L'Explorateur (Fiches, Lieux, Chapitres)
        self.dock_explorer = QDockWidget("Navigation & Éléments", self)
        # On autorise l'auteur à le glisser à gauche ou à droite
        self.dock_explorer.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.explorer = QTreeWidget()
        self.explorer.setHeaderLabel("UBK - Projet")
        QTreeWidgetItem(self.explorer, ["index.umd"])
        QTreeWidgetItem(self.explorer, ["chap01.umd"])
        
        self.dock_explorer.setWidget(self.explorer)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_explorer)


        # 3. VOLET MOBILE DROIT : L'AST de Debug
        self.dock_ast = QDockWidget("Structure AST (Debug)", self)
        self.dock_ast.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)

        self.ast_view = QPlainTextEdit()
        self.ast_view.setReadOnly(True)

        self.dock_ast.setWidget(self.ast_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_ast)


        # -------- Connexions --------
        self.editor.textChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def update_preview(self):

        text = self.editor.toPlainText()

        # -------- AST Document --------
        doc = parse_document(text)

        self.ast_view.setPlainText(
            json.dumps(
                doc,
                indent=2,
                ensure_ascii=False
            )
        )
    
        # -------- Rendu HTML --------
        content = render_document(doc)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}

div {{
    white-space: pre-wrap;
}}

.umd-space {{
    height: 2em;
}}

hr {{
    margin: 1em 0;
}}

/* --- Separators --- */
.sep-double {{ border: none; border-top: 3px double #888; }}
.sep-dotted {{ border: none; border-top: 2px dotted #888; }}
.sep-dashed {{ border: none; border-top: 2px dashed #888; }}
.sep-wave {{ border: none; text-align: center; }}
.sep-repeat {{ margin: 1em 0; text-align: center; color: #666; font-family: monospace; overflow: hidden; }}

/* --- Inline Code --- */
.inline-code {{
    background: #f3f3f3;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 4px;
    font-family: Consolas, monospace;
}}

/* --- Nouveau système de bloc de code --- */
.code-block-container {{
    margin: 1.5em 0;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    overflow: hidden;
    background-color: #ffffff;
    width: 100%;
}}

.code-block-header {{
    background-color: #f6f8fa;
    padding: 6px 12px;
    border-bottom: 1px solid #e0e0e0;
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
    counter-reset: line; /* Le fameux compteur moderne */
}}

.code-line {{
    display: block;
    padding-left: 55px;
    padding-right: 12px;
    position: relative;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    color: #333;
    text-align: left;
}}

.code-line::before {{
    counter-increment: line;
    content: counter(line);
    position: absolute;
    left: 0;
    top: 0;
    width: 40px;
    height: 100%;
    background: #f0f0f0;
    color: #999;
    text-align: right;
    padding-right: 8px;
    border-right: 1px solid #ddd;
    user-select: none;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
</style>
</head>
<body>
{content}
</body>
</html>
"""

        self.preview.setHtml(html)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
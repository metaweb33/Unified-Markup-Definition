#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum ASTNode {
    Heading { level: u8, line: usize, content: String },
    Paragraph { line: usize, indented: bool, content: String },
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ASTDocument {
    pub r#type: String,
    pub children: Vec<ASTNode>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ParseResult {
    pub html: String,
    pub ast: ASTDocument,
}

#[derive(Debug, PartialEq, Clone)]
enum StyleTag {
    Italic,
    Bold,
    UnderlineSimple,
    UnderlineThick,
    UnderlineDouble,
    Superscript,
    Subscript,
}

fn strip_umd_markup(text: &str) -> String {
    let mut clean = text.to_string();
    let tokens = [
        "***", "/**", "/*", "**", "*", 
        "___", "__", "_", "/_", 
        "/&", "{/}", "/^", "/~", "^", "~"
    ];
    for token in tokens {
        clean = clean.replace(token, "");
    }
    clean.trim().to_string()
}

fn parse_umd_line_to_html(line: &str) -> String {
    let chars: Vec<char> = line.chars().collect();
    let len = chars.len();
    let mut i = 0;
    
    let mut html = String::new();
    let mut active_tags: Vec<StyleTag> = Vec::new();

    let close_tag = |tag: &StyleTag| -> &'static str {
        match tag {
            StyleTag::Italic => "</em>",
            StyleTag::Bold => "</strong>",
            StyleTag::UnderlineSimple | StyleTag::UnderlineThick | StyleTag::UnderlineDouble => "</span>",
            StyleTag::Superscript => "</sup>",
            StyleTag::Subscript => "</sub>",
        }
    };

    let close_all = |active_tags: &mut Vec<StyleTag>, html: &mut String| {
        while let Some(tag) = active_tags.pop() {
            html.push_str(close_tag(&tag));
        }
    };

    while i < len {
        // 1. Fermeture générale (/& ou {/})
        if (i + 1 < len && chars[i] == '/' && chars[i + 1] == '&') ||
           (i + 2 < len && chars[i] == '{' && chars[i + 1] == '/' && chars[i + 2] == '}') {
            close_all(&mut active_tags, &mut html);
            i += if chars[i] == '{' { 3 } else { 2 };
            continue;
        }

        // 2. Fermetures explicites (/**, /*, /_, /^, /~)
        if chars[i] == '/' {
            if i + 2 < len && chars[i + 1] == '*' && chars[i + 2] == '*' {
                if let Some(pos) = active_tags.iter().rposition(|t| *t == StyleTag::Bold) {
                    let tag = active_tags.remove(pos);
                    html.push_str(close_tag(&tag));
                }
                i += 3;
                continue;
            }
            if i + 1 < len {
                let next = chars[i + 1];
                let target = match next {
                    '*' => Some(StyleTag::Italic),
                    '_' => active_tags.iter().rev().find(|t| matches!(t, StyleTag::UnderlineSimple | StyleTag::UnderlineThick | StyleTag::UnderlineDouble)).cloned(),
                    '^' => Some(StyleTag::Superscript),
                    '~' => Some(StyleTag::Subscript),
                    _ => None,
                };

                if let Some(tag) = target {
                    if let Some(pos) = active_tags.iter().rposition(|t| *t == tag) {
                        let removed = active_tags.remove(pos);
                        html.push_str(close_tag(&removed));
                    }
                    i += 2;
                    continue;
                }
            }
        }

        // 3. Ouvertures : Exposant / Indice (Réinitialisation forcée du style si nécessaire)
        if chars[i] == '^' {
            active_tags.push(StyleTag::Superscript);
            html.push_str("<sup style=\"font-weight: normal; font-style: normal;\">");
            i += 1;
            continue;
        }

        if chars[i] == '~' {
            active_tags.push(StyleTag::Subscript);
            html.push_str("<sub style=\"font-weight: normal; font-style: normal;\">");
            i += 1;
            continue;
        }

        // 4. Ouvertures Gras / Emphase
        if chars[i] == '*' {
            if i + 2 < len && chars[i + 1] == '*' && chars[i + 2] == '*' {
                active_tags.push(StyleTag::Bold);
                active_tags.push(StyleTag::Italic);
                html.push_str("<strong><em>");
                i += 3;
            } else if i + 1 < len && chars[i + 1] == '*' {
                active_tags.push(StyleTag::Bold);
                html.push_str("<strong>");
                i += 2;
            } else {
                active_tags.push(StyleTag::Italic);
                html.push_str("<em>");
                i += 1;
            }
            continue;
        }

        // 5. Ouvertures Soulignements
        if chars[i] == '_' {
            if i + 2 < len && chars[i + 1] == '_' && chars[i + 2] == '_' {
                active_tags.push(StyleTag::UnderlineDouble);
                html.push_str("<span style=\"text-decoration: underline double;\">");
                i += 3;
            } else if i + 1 < len && chars[i + 1] == '_' {
                active_tags.push(StyleTag::UnderlineThick);
                html.push_str("<span style=\"text-decoration: underline 2px;\">");
                i += 2;
            } else {
                active_tags.push(StyleTag::UnderlineSimple);
                html.push_str("<span style=\"text-decoration: underline;\">");
                i += 1;
            }
            continue;
        }

        html.push(chars[i]);
        i += 1;
    }

    close_all(&mut active_tags, &mut html);
    html
}

#[tauri::command]
fn parse_umd(text: String) -> ParseResult {
    let mut html_output = String::new();
    let mut ast_children = Vec::new();

    // Tailles explicites des titres H1..H6 pour éviter la surcharge CSS externe
    let font_sizes = ["2.2em", "1.8em", "1.5em", "1.3em", "1.1em", "0.9em"];

    for (index, line) in text.lines().enumerate() {
        let line_num = index + 1;
        let trimmed = line.trim();

        if trimmed.starts_with('#') {
            let mut level = 1u8;
            let mut raw_content = trimmed;

            if trimmed.starts_with("#1") { level = 1; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with("#2") { level = 2; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with("#3") { level = 3; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with("#4") { level = 4; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with("#5") { level = 5; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with("#6") { level = 6; raw_content = &trimmed[2..]; }
            else if trimmed.starts_with('#') { level = 1; raw_content = &trimmed[1..]; }

            let clean_text = raw_content.trim();
            let parsed_content = parse_umd_line_to_html(clean_text);
            let size = font_sizes.get((level - 1) as usize).unwrap_or(&"1em");

            html_output.push_str(&format!(
                "<h{} style=\"font-size: {}; margin: 12px 0 6px 0; font-weight: bold; text-transform: none;\">{}</h{}>\n",
                level, size, parsed_content, level
            ));

            ast_children.push(ASTNode::Heading {
                level,
                line: line_num,
                content: strip_umd_markup(clean_text),
            });
        } else {
            let is_indented = line.starts_with("    ") || line.starts_with('\t');
            let parsed_content = parse_umd_line_to_html(line);

            let padding = if is_indented { "padding-left: 24px;" } else { "" };
            let display_content = if parsed_content.is_empty() { "&nbsp;".to_string() } else { parsed_content };

            html_output.push_str(&format!(
                "<p style=\"margin: 4px 0; {}\">{}</p>\n",
                padding, display_content
            ));

            ast_children.push(ASTNode::Paragraph {
                line: line_num,
                indented: is_indented,
                content: strip_umd_markup(line),
            });
        }
    }

    ParseResult {
        html: html_output,
        ast: ASTDocument {
            r#type: "Document".to_string(),
            children: ast_children,
        },
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![parse_umd])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
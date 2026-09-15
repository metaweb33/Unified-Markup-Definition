console.log('Script UMD Editor chargé !');

const { invoke } = window.__TAURI__.core; // Utiliser .core pour Tauri v2 (ou window.__TAURI__.tauri selon ton setup)

const editor = document.getElementById('editor');
const htmlPreview = document.getElementById('html-preview');
const astPreview = document.getElementById('ast-preview');

// Fonction d'actualisation via le backend Rust
async function update() {
  if (!editor) return;
  const text = editor.value;

  try {
    const result = await invoke('parse_umd', { text });
    htmlPreview.innerHTML = result.html;
    astPreview.textContent = JSON.stringify(result.ast, null, 2);
  } catch (err) {
    console.error("Erreur d'invocation Rust:", err);
  }
}

if (editor && htmlPreview && astPreview) {
  // Écouteur de saisie clavier
  editor.addEventListener('input', update);

  // Gestion du Drag & Drop pour les fichiers .umd
  editor.addEventListener('dragover', (e) => e.preventDefault());
  editor.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.umd') || file.name.endsWith('.txt'))) {
      const reader = new FileReader();
      reader.onload = (event) => {
        editor.value = event.target.result;
        update(); // Lance le parsing Rust sur le contenu du fichier chargé
      };
      reader.readAsText(file);
    }
  });

  // Premier rendu au chargement
  update();
}
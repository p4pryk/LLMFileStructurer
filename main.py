import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QGuiApplication


class PromptAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM File Structurer")

        # Lista załączonych plików: lista krotek (ścieżka_do_wyświetlenia, zawartość)
        self.attached_files = []
        self.tree = {}  # Struktura dla hierarchii plików

        # Główny widget i layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Etykieta informacyjna
        label = QLabel(
            "<b>Welcome to LLM File Structurer!</b><br><br>"
            "Extract and structure text/code from files and folders to create a well-organized input for language models.<br><br>"
            "<b>How it works:</b><br>"
            "- 📂 <b>Attach files or folders</b> – The program extracts text from them.<br>"
            "- 🌳 <b>Generates a hierarchy</b> – A structured tree view of files helps models understand context.<br>"
            "- 📜 <b>Includes file contents</b> – The extracted text is formatted for easier processing.<br>"
            "- 📋 <b>Copy structured output</b> – Get everything in a single format for easy input into AI models.<br>"
            "- ❌ <b>Clear all</b> – Reset and start fresh.<br><br>"
            "🚀 Start by adding files or folders!"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        # Duży obszar tekstowy
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type or paste your prompt here...")
        layout.addWidget(self.text_edit)

        # Lista plików
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        # Kontener dla przycisków
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Przycisk "Attach Files"
        self.attach_button = QPushButton("Attach Files")
        self.attach_button.setToolTip("Select one or more files to include in your prompt.")
        self.attach_button.clicked.connect(self.attach_files)
        button_layout.addWidget(self.attach_button)

        # Przycisk "Attach Folder"
        self.attach_folder_button = QPushButton("Attach Folder")
        self.attach_folder_button.setToolTip("Select a folder to include all its (non-hidden) files.")
        self.attach_folder_button.clicked.connect(self.attach_folder)
        button_layout.addWidget(self.attach_folder_button)

        # Przycisk "Copy"
        self.copy_button = QPushButton("Copy Prompt")
        self.copy_button.setToolTip("Generate the final prompt with file structure and contents, then copy it.")
        self.copy_button.clicked.connect(self.copy_prompt)
        button_layout.addWidget(self.copy_button)

        # Przycisk "Clear"
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setToolTip("Clear the text area and remove all attached files.")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

    def attach_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files to Attach", "", "All Files (*.*)")
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    display_path = os.path.basename(path)
                    self.attached_files.append((display_path, content))
                    self.files_list.addItem(QListWidgetItem(display_path))
                except Exception:
                    pass

    def attach_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Attach", "")
        if folder:
            for root, dirs, files in os.walk(folder):
                # Pomijamy ukryte foldery i "venv"
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != "venv"]
                for file in files:
                    if file.startswith('.') or "tfstate" in file:
                        continue  # Pomijamy ukryte pliki i pliki zawierające "tfstate"
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            rel_path = os.path.relpath(file_path, folder)
                            self.attached_files.append((rel_path, content))
                            self.files_list.addItem(QListWidgetItem(rel_path))
                        except Exception:
                            pass

    def copy_prompt(self):
        if not self.attached_files:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText("No files attached")
            return

        # Część 1: "Drzewko" – lista nazw/ścieżek plików
        file_names = [path for path, _ in self.attached_files]
        tree_view = "\n".join(file_names)

        # Część 2: Bloki z zawartością plików w zadanym formacie
        file_blocks = "\n\n".join([f"<{path}>\n{content}\n</{path}>" for path, content in self.attached_files])

        # Łączymy obie części – najpierw drzewko, potem zawartość
        structured_text = f"{tree_view}\n\n{file_blocks}"
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(structured_text)

    def clear_all(self):
        self.text_edit.clear()
        self.files_list.clear()
        self.attached_files.clear()
        self.tree.clear()  # Reset the file hierarchy


def main():
    app = QApplication(sys.argv)
    window = PromptAssistant()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

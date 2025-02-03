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

        # List of attached files: stores tuples (display_path, content)
        self.attached_files = []

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Informational label
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

        # Large text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type or paste your prompt here...")
        layout.addWidget(self.text_edit)

        # List of files
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        # Container for buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # "Attach Files" button
        self.attach_button = QPushButton("Attach Files")
        self.attach_button.setToolTip("Select one or more files to include in your prompt.")
        self.attach_button.clicked.connect(self.attach_files)
        button_layout.addWidget(self.attach_button)

        # "Attach Folder" button
        self.attach_folder_button = QPushButton("Attach Folder")
        self.attach_folder_button.setToolTip("Select a folder to include all its (non-hidden) files.")
        self.attach_folder_button.clicked.connect(self.attach_folder)
        button_layout.addWidget(self.attach_folder_button)

        # "Copy" button
        self.copy_button = QPushButton("Copy Prompt")
        self.copy_button.setToolTip("Generate the final prompt with file structure and contents, then copy it.")
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)

        # "Clear" button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setToolTip("Clear the text area and remove all attached files.")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

    def attach_files(self):
        """
        Opens a file selection dialog allowing the user to pick one or more files.
        The content of each file is read, stored in attached_files, 
        and added to the list view for reference.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Attach",
            "",
            "All Files (*.*)"
        )

        for path in file_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    display_path = os.path.basename(path)
                    self.attached_files.append((display_path, content))
                    self.files_list.addItem(QListWidgetItem(display_path))
                except Exception as e:
                    # You could handle or log the error here.
                    pass

    def attach_folder(self):
        """
        Opens a folder selection dialog. Recursively goes through all files in the selected folder, 
        skipping hidden files/folders (those starting with a dot) and files that contain "tfstate" in their names.
        Each file is read and stored, and a relative path (to the selected folder) is shown in the list.
        """
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Attach",
            ""
        )
        if folder:
            for root, dirs, files in os.walk(folder):
                # Skip hidden folders
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    # Pomijamy ukryte pliki oraz te, które zawierają "tfstate" (np. terraform.tfstate, terraform.tfstate.backup)
                    if file.startswith('.') or "tfstate" in file:
                        continue  # Skip hidden files and files containing "tfstate"
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            # Calculate the path relative to the selected folder
                            rel_path = os.path.relpath(file_path, folder)
                            self.attached_files.append((rel_path, content))
                            self.files_list.addItem(QListWidgetItem(rel_path))
                        except Exception as e:
                            # If the file cannot be read, skip it
                            pass


    def copy_text(self):
        """
        Combines the user's prompt text, a textual representation of the attached file structure,
        and the contents of all attached files into a single string. The resulting text is then 
        copied to the system clipboard.
        """
        user_text = self.text_edit.toPlainText()

        # Build the hierarchy tree based on the displayed file paths
        tree = {}
        for display_path, _ in self.attached_files:
            parts = os.path.normpath(display_path).split(os.sep)
            current = tree
            for part in parts[:-1]:
                current = current.setdefault(part, {"__files__": []})
            current.setdefault("__files__", []).append(parts[-1])

        def format_tree(t, indent=0):
            lines = []
            # Add files at the current level
            if "__files__" in t:
                for f in sorted(t["__files__"]):
                    lines.append(" " * indent + f)
            # Recursively add folders
            for key in sorted(k for k in t.keys() if k != "__files__"):
                lines.append(" " * indent + key + "/")
                lines.extend(format_tree(t[key], indent + 2))
            return lines

        tree_lines = format_tree(tree)
        tree_text = "\n".join(tree_lines)

        final_text = (
            user_text +
            "\n<tree>\n" +
            tree_text +
            "\n</tree>\n<files>\n"
        )

        for display_path, content in self.attached_files:
            final_text += f"\t<{display_path}>\n"
            for line in content.splitlines():
                final_text += f"\t\t{line}\n"
            final_text += f"\t</{display_path}>\n"

        final_text += "</files>\n"

        # Copy final text to clipboard
        QGuiApplication.clipboard().setText(final_text)

    def clear_all(self):
        """
        Clears the text edit field, empties the attached_files list, 
        and removes all items from the files_list widget.
        """
        self.text_edit.clear()
        self.files_list.clear()
        self.attached_files.clear()


def main():
    app = QApplication(sys.argv)
    window = PromptAssistant()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

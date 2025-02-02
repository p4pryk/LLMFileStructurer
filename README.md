# LLM File Structurer

## Description  
**LLM File Structurer** extracts and organizes text/code from files and folders to generate a structured input for language models. It helps AI models understand the hierarchy of files and their contents, even when they do not support direct file attachments.

### Key Features:  
- 📂 **Extracts text from files and folders**  
- 🌳 **Generates a hierarchical file structure**  
- 📜 **Includes file contents for context**  
- 📋 **Copies structured output for AI processing**  
- ❌ **Clears all data easily**  

---

## Installation  

### 1. Create a Virtual Environment  
Using a virtual environment is recommended to manage dependencies and prevent conflicts with other packages. Run the following commands:  

```bash
python -m venv env
```

Activate the virtual environment:  
- On Linux/macOS:  
  ```bash
  source env/bin/activate
  ```
- On Windows:  
  ```bash
  .\env\Scripts\activate
  ```

### 2. Install Dependencies  
Install the required dependencies listed in `requirements.txt`:  

```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:  
- `PyQt5 == 5.15.11` – For building the graphical user interface.  

---

## Running the Application  

After setting up the environment and installing dependencies, run the application with:  

```bash
python main.py
```


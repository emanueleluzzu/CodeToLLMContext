# CodeToLLMContext 🧑💻

CodeToLLMContext is a powerful tool that extracts and formats your local code into structured context perfect for sharing with Large Language Models (LLMs) like ChatGPT, Claude, or any AI assistant.

## ✨ Features

- 📁 **Complete project mode**: Extracts code from all project files
- 📄 **Single file mode**: Processes only a specific file (with project structure for context)
- 🖥️ **Graphical interface** with Textual for interactive navigation
- 💻 **CLI interface** for automation and scripting
- 🚫 **.gitignore support** to automatically exclude files
- 🎨 **Syntax highlighting** for different programming languages
- ⚙️ **Customizable configuration** via `settings.py`

## 🚀 Installation

### Option 1: Development/Portable Installation

#### Using pip
```bash
# Clone the repository
git clone <repository-url>
cd CodeToLLMContext

# Install dependencies
pip install textual pathlib pyinstaller
```

#### Using uv (faster alternative)
```bash
# Clone the repository
git clone <repository-url>
cd CodeToLLMContext

# Initialize project and install dependencies
uv init
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add textual pathlib pyinstaller

# Run the tool
uv run main.py --gui
```

### Option 2: System Installation (Standalone Executable)

⚠️ **Important**: Configure `settings.py` first, as it cannot be modified after installation!

#### Using pip
```bash
# 1. Clone and setup
git clone <repository-url>
cd CodeToLLMContext
pip install textual pathlib pyinstaller

# 2. Configure settings.py to your preferences
# Edit the file to customize directories, extensions, etc.

# 3. Build standalone executable
pyinstaller --onefile --noconsole --name CodeToLLMContext main.py

# 4. The executable will be in dist/CodeToLLMContext
# Copy it to your system PATH or desired location
```

#### Using uv
```bash
# 1. Clone and setup
git clone <repository-url>
cd CodeToLLMContext
uv init
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add textual pathlib pyinstaller

# 2. Configure settings.py to your preferences
# Edit the file to customize directories, extensions, etc.

# 3. Build standalone executable
uv run pyinstaller --onefile --noconsole --name CodeToLLMContext main.py

# 4. The executable will be in dist/CodeToLLMContext
# Copy it to your system PATH or desired location
```

**System Installation Benefits:**
- ✅ Run from anywhere: `CodeToLLMContext` command available globally
- ✅ No Python environment needed
- ✅ Self-contained executable
- ⚠️ Settings are frozen at build time

## 📖 Usage

### Graphical Interface

```bash
python main.py --gui
```

**GUI Controls:**
- 📂 **Select directory**: Click on a folder in the left tree
- 📄 **Single file mode**: Enable checkbox and click on a file
- 🚀 **Generate context**: Enter prompt and press `G` or the button
- 🔄 **Reset**: Press `R` to reset selections
- ❌ **Exit**: Press `ESC` or the exit button

### CLI Interface

#### Complete project
```bash
# Current directory
python main.py

# Specific directory
python main.py /path/to/project

# With custom parameters
python main.py /path/to/project --max-chars 10000 --output my_context.md
```

#### Single file
```bash
# Specific file
python main.py /path/to/file.py --file

# With parameters
python main.py /path/to/file.py --file --max-chars 8000 --output file_context.md
```

### CLI Parameters

- `path`: Project or file path (default: current directory)
- `--file`: Treat path as single file
- `--max-chars`: Character limit per file (default: 5000)
- `--output`: Output file name (default: context.md)
- `--gui`: Launch graphical interface

## ⚙️ Configuration

⚠️ **For System Installation**: Configure `settings.py` BEFORE building the executable, as settings cannot be changed after installation.

Create or modify the `settings.py` file to customize behavior:

```python
def skip_dirs():
    """Directories to exclude"""
    return {".git", ".venv", "node_modules", "__pycache__", "build", "dist"}

def skip_files():
    """Files to exclude (names or extensions)"""
    return {".gitignore", ".pyc", ".exe", "settings.py"}

def allowed_extensions():
    """File extensions to include"""
    return {".py", ".js", ".cpp", ".h", ".md", ".txt", ".json"}

def max_file_size():
    """Character limit per file"""
    return 5000

def css():
    """Custom CSS for GUI"""
    return """
    /* Your custom CSS here */
    """
```

## 📋 Generated Output

The `context.md` file includes:

### Complete Project Mode
```markdown
# 🧑💻 CONTEXT: `project_name`

## ℹ️ PROJECT INFO
- **Path**: `/path/to/project`
- **Mode**: Complete project
- **Included extensions**: .py, .js, .cpp, .h
- ...

## 📁 STRUCTURE
```
src/
    main.py
    utils.py
docs/
    README.md
```

## 📝 CODE

### `src/main.py`
```python
# File content...
```

## ❓ PROMPT
Your question here...
```

### Single File Mode
```markdown
# 🧑💻 CONTEXT: `file.py` (📁 project_name)

## ℹ️ PROJECT INFO
- **Path**: `/path/to/project`
- **Selected file**: `file.py`
- **Mode**: Single file
- ...

## 📁 STRUCTURE
```
src/
    main.py
    >>> utils.py <<<  # Selected file highlighted
docs/
    README.md
```

## 📝 CODE

### `src/utils.py` ⭐ (Selected file)
```python
# Only the content of the selected file
```

## ❓ PROMPT
Your question about the specific file...
```

### Development Mode (Portable)
- ✅ Settings can be modified anytime
- ✅ Easy debugging and customization
- ✅ Python environment required
- 📁 Run from project directory

### System Installation (Standalone)
- ✅ Global access from any directory
- ✅ No Python dependencies
- ✅ Fast execution
- ⚠️ Settings frozen at build time
- 💡 Perfect for daily use

## 🎯 Use Cases

### Complete Project
- 🔍 General project analysis
- 🐛 Debugging issues involving multiple files
- 📚 Architecture documentation
- 🔄 Large-scale refactoring

### Single File
- 🎯 Focus on specific function/class
- 🔧 Debug error in particular file
- 📝 Targeted code review
- 💡 Specific optimization suggestions

## 🔑 Keyboard Shortcuts (GUI)

- `G`: Generate context
- `C`: Change directory
- `R`: Reset selections
- `ESC`: Exit application

## 🛠️ Supported Languages

- Python (`.py`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Markdown (`.md`)
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)
- CSS/SCSS (`.css`, `.scss`)
- HTML (`.html`)
- SQL (`.sql`)
- Shell (`.sh`, `.bat`)
- QML (`.qml`)

## 📄 License

This project is released under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

---

**Happy Coding!** 🚀

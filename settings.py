def skip_dirs():
    """Directories to exclude from scanning"""
    return {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        "build",
        "dist",
        ".vscode",
        ".idea",
        "target",
        "bin",
        "obj",
        ".pytest_cache"
    }

def skip_files():
    """Files to exclude from scanning (full name or extension)"""
    return {
        ".gitignore",
        ".pyc",
        ".exe",
        ".dll",
        ".so",
        "settings.py",  # This file itself
        "context.md",   # Generated output
        ".DS_Store",    # macOS
        "Thumbs.db",    # Windows
        ".env",         # Environment file
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
        "Pipfile.lock"
    }

def allowed_extensions():
    """Allowed file extensions"""
    return {
        ".cpp", ".c", ".cc", ".cxx",
        ".h", ".hpp", ".hxx",
        ".py", ".pyx",
        ".js", ".jsx", ".ts", ".tsx",
        ".md", ".txt", ".rst",
        ".qml", ".qrc",
        ".cmake", ".CMakeLists.txt",
        ".json", ".yaml", ".yml",
        ".sql", ".sh", ".bat",
        ".css", ".scss", ".less",
        ".html", ".htm"
    }

def max_file_size():
    """Maximum file size in characters"""
    return 10000

def css():
    """CSS for Textual interface"""
    return """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 1;
    }

    #left-panel {
        width: 100%;
        height: 100%;
    }

    #tree-view {
        height: 70%;
        border: solid $accent;
        margin-bottom: 1;
    }

    #project-info {
        height: 30%;
        border: solid $primary;
        padding: 1;
    }

    #right-panel {
        width: 100%;
        height: 100%;
    }

    #code-view {
        height: 70%;
        border: solid $accent;
        overflow: auto;
        margin-bottom: 1;
    }

    #input-area {
        height: 30%;
    }

    #prompt-input {
        margin-bottom: 1;
    }

    #buttons {
        layout: horizontal;
        height: 3;
    }

    Button {
        width: 1fr;
        margin: 0 1;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }

    .warning {
        color: $warning;
    }

    .info {
        color: $text;
    }

    #tree-view:focus {
        border: thick $accent;
    }

    #code-view {
        scrollbar-size: 1 1;
    }
    """

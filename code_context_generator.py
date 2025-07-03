#!/usr/bin/env python3
import os
from pathlib import Path

# Import settings, with fallback if file doesn't exist
try:
    from settings import skip_dirs, skip_files, allowed_extensions, max_file_size
except ImportError:
    def skip_dirs():
        return {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", ".vscode"}
    def skip_files():
        return {".gitignore", ".pyc", ".exe", ".dll", ".so", "settings.py"}
    def allowed_extensions():
        return {".cpp", ".h", ".py", ".js", ".md", ".txt", ".qml"}
    def max_file_size():
        return 5000

class CodeContextGenerator:
    def __init__(self, project_path=None, single_file=False):
        self.single_file = single_file
        self.selected_file = None

        if project_path:
            path = Path(project_path)
            if path.is_file():
                self.single_file = True
                self.selected_file = path
                self.project_path = path.parent
            else:
                self.project_path = path
        else:
            self.project_path = self._ask_path()

        self.exclude_dirs = skip_dirs()
        self.exclude_files = skip_files()
        self.allowed_ext = allowed_extensions()
        self.max_chars = max_file_size()

    def _ask_path(self):
        """Ask for path via terminal with single file option"""
        while True:
            path_input = input("Enter project/file path (or '.' for current folder): ").strip()
            path = Path('.' if path_input == '' else path_input)

            if path.exists():
                if path.is_file():
                    choice = input(f"📄 You selected a file: {path.name}. Do you want to process only this file? (y/N): ").strip().lower()
                    if choice in ['y', 'yes', 's', 'si']:
                        self.single_file = True
                        self.selected_file = path
                        return path.parent
                    else:
                        return path.parent
                else:
                    return path.absolute()
            print(f"❌ Invalid path: {path}. Try again.")

    def set_single_file(self, file_path):
        """Set a single file for processing"""
        file_path = Path(file_path)
        if file_path.exists() and file_path.is_file():
            self.single_file = True
            self.selected_file = file_path
            self.project_path = file_path.parent
            return True
        return False

    def _load_gitignore(self):
        """Load .gitignore rules if present"""
        gitignore = self.project_path / ".gitignore"
        if gitignore.exists():
            with open(gitignore, encoding="utf-8") as f:
                return {line.strip() for line in f if line.strip() and not line.startswith("#")}
        return set()

    def _should_exclude(self, path):
        """Check if a path should be excluded"""
        path_obj = Path(path)

        # Check directories
        if path_obj.is_dir():
            return path_obj.name in self.exclude_dirs

        # Check files by full name
        if path_obj.name in self.exclude_files:
            return True

        # Check files by extension
        if path_obj.suffix in self.exclude_files:
            return True

        # Check if it's inside an excluded directory
        parts = path_obj.parts
        return any(part in self.exclude_dirs for part in parts)

    def _should_include_file(self, file_path):
        """Determine if a file should be included in output"""
        path_obj = Path(file_path)

        # If we're processing a single file and this is that file, always include it
        if self.single_file and self.selected_file and path_obj == self.selected_file:
            return True

        # Must have an allowed extension
        if path_obj.suffix not in self.allowed_ext:
            return False

        # Must not be excluded
        if self._should_exclude(path_obj):
            return False

        # Must not be in an excluded directory
        rel_path = path_obj.relative_to(self.project_path)
        if any(part in self.exclude_dirs for part in rel_path.parts):
            return False

        return True

    def generate_context(self, output_file="context.md", max_chars=None):
        """Generate the context file"""
        if max_chars is None:
            max_chars = self.max_chars

        gitignore_rules = self._load_gitignore()

        with open(output_file, "w", encoding="utf-8") as f:
            # Header
            if self.single_file and self.selected_file:
                f.write(f"# 🧑💻 CONTEXT: `{self.selected_file.name}` (📁 {self.project_path.name})\n\n")
            else:
                f.write(f"# 🧑💻 CONTEXT: `{self.project_path.name}`\n\n")

            # Project information
            f.write("## ℹ️ PROJECT INFO\n")
            f.write(f"- **Path**: `{self.project_path}`\n")
            if self.single_file and self.selected_file:
                f.write(f"- **Selected file**: `{self.selected_file.name}`\n")
                f.write(f"- **Mode**: Single file\n")
            else:
                f.write(f"- **Mode**: Complete project\n")
            f.write(f"- **Included extensions**: {', '.join(sorted(self.allowed_ext))}\n")
            f.write(f"- **Excluded directories**: {', '.join(sorted(self.exclude_dirs))}\n")
            f.write(f"- **Excluded files**: {', '.join(sorted(self.exclude_files))}\n")
            f.write(f"- **Character limit per file**: {max_chars}\n\n")

            # Folder tree (always included for context)
            f.write("## 📁 STRUCTURE\n```\n")
            self._write_tree_structure(f, self.project_path, gitignore_rules)
            f.write("```\n\n")

            # File content
            f.write("## 📝 CODE\n")
            files_included = 0

            if self.single_file and self.selected_file:
                # Process only the selected file
                if self._should_include_file(self.selected_file):
                    rel_path = self.selected_file.relative_to(self.project_path)
                    self._write_file_content(f, self.selected_file, rel_path, max_chars)
                    files_included = 1
                else:
                    f.write(f"⚠️ The selected file `{self.selected_file.name}` doesn't meet the inclusion criteria.\n")
            else:
                # Process all project files
                for root, _, files in os.walk(self.project_path):
                    root_path = Path(root)

                    # Skip excluded directories
                    if self._should_exclude(root_path):
                        continue

                    for file in files:
                        file_path = root_path / file

                        if self._should_include_file(file_path):
                            rel_path = file_path.relative_to(self.project_path)

                            # Also check gitignore rules
                            if not any(rule in str(rel_path) for rule in gitignore_rules):
                                self._write_file_content(f, file_path, rel_path, max_chars)
                                files_included += 1

            # Statistics
            f.write(f"\n## 📊 STATISTICS\n")
            f.write(f"- **Files included**: {files_included}\n")
            if self.single_file and self.selected_file:
                f.write(f"- **Mode**: Single file ({self.selected_file.name})\n")
            f.write(f"- **Base directory**: {self.project_path}\n\n")

            # User prompt
            if self.single_file and self.selected_file:
                prompt = input(f"\n💡 Enter your question/request for the file '{self.selected_file.name}': ")
            else:
                prompt = input("\n💡 Enter your question/request: ")
            f.write(f"## ❓ PROMPT\n{prompt}\n")

        print(f"\n✅ File generated: `{output_file}`")
        if self.single_file and self.selected_file:
            print(f"📄 File processed: {self.selected_file.name}")
        else:
            print(f"📁 {files_included} files included")
        print("📋 Copy the content and paste it in the chat!")

    def generate_context_with_prompt(self, prompt, output_file="context.md", max_chars=None):
        """Generate the context file with a provided prompt"""
        if max_chars is None:
            max_chars = self.max_chars

        gitignore_rules = self._load_gitignore()

        with open(output_file, "w", encoding="utf-8") as f:
            # Header
            if self.single_file and self.selected_file:
                f.write(f"# 🧑💻 CONTEXT: `{self.selected_file.name}` (📁 {self.project_path.name})\n\n")
            else:
                f.write(f"# 🧑💻 CONTEXT: `{self.project_path.name}`\n\n")

            # Project information
            f.write("## ℹ️ PROJECT INFO\n")
            f.write(f"- **Path**: `{self.project_path}`\n")
            if self.single_file and self.selected_file:
                f.write(f"- **Selected file**: `{self.selected_file.name}`\n")
                f.write(f"- **Mode**: Single file\n")
            else:
                f.write(f"- **Mode**: Complete project\n")
            f.write(f"- **Included extensions**: {', '.join(sorted(self.allowed_ext))}\n")
            f.write(f"- **Excluded directories**: {', '.join(sorted(self.exclude_dirs))}\n")
            f.write(f"- **Excluded files**: {', '.join(sorted(self.exclude_files))}\n")
            f.write(f"- **Character limit per file**: {max_chars}\n\n")

            # Folder tree (always included for context)
            f.write("## 📁 STRUCTURE\n```\n")
            self._write_tree_structure(f, self.project_path, gitignore_rules)
            f.write("```\n\n")

            # File content
            f.write("## 📝 CODE\n")
            files_included = 0

            if self.single_file and self.selected_file:
                # Process only the selected file
                if self._should_include_file(self.selected_file):
                    rel_path = self.selected_file.relative_to(self.project_path)
                    self._write_file_content(f, self.selected_file, rel_path, max_chars)
                    files_included = 1
                else:
                    f.write(f"⚠️ The selected file `{self.selected_file.name}` doesn't meet the inclusion criteria.\n")
            else:
                # Process all project files
                for root, _, files in os.walk(self.project_path):
                    root_path = Path(root)

                    # Skip excluded directories
                    if self._should_exclude(root_path):
                        continue

                    for file in files:
                        file_path = root_path / file

                        if self._should_include_file(file_path):
                            rel_path = file_path.relative_to(self.project_path)

                            # Also check gitignore rules
                            if not any(rule in str(rel_path) for rule in gitignore_rules):
                                self._write_file_content(f, file_path, rel_path, max_chars)
                                files_included += 1

            # Statistics
            f.write(f"\n## 📊 STATISTICS\n")
            f.write(f"- **Files included**: {files_included}\n")
            if self.single_file and self.selected_file:
                f.write(f"- **Mode**: Single file ({self.selected_file.name})\n")
            f.write(f"- **Base directory**: {self.project_path}\n\n")

            # Provided prompt
            f.write(f"## ❓ PROMPT\n{prompt}\n")

        print(f"\n✅ File generated: `{output_file}`")
        if self.single_file and self.selected_file:
            print(f"📄 File processed: {self.selected_file.name}")
        else:
            print(f"📁 {files_included} files included")
        print("📋 Copy the content and paste it in the chat!")

    def _write_tree_structure(self, f, start_path, gitignore_rules, prefix="", max_depth=3, current_depth=0):
        """Write the tree structure of directories"""
        if current_depth >= max_depth:
            return

        try:
            items = sorted(start_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            for item in items:
                if self._should_exclude(item):
                    continue

                # Check gitignore
                rel_path = item.relative_to(self.project_path)
                if any(rule in str(rel_path) for rule in gitignore_rules):
                    continue

                if item.is_dir():
                    f.write(f"{prefix}{item.name}/\n")
                    self._write_tree_structure(f, item, gitignore_rules, prefix + "    ", max_depth, current_depth + 1)
                else:
                    if item.suffix in self.allowed_ext and item.name not in self.exclude_files:
                        # Highlight the selected file if in single file mode
                        if self.single_file and self.selected_file and item == self.selected_file:
                            f.write(f"{prefix}>>> {item.name} <<<\n")
                        else:
                            f.write(f"{prefix}{item.name}\n")
        except PermissionError:
            f.write(f"{prefix}[Access denied]\n")

    def _write_file_content(self, f, file_path, rel_path, max_chars):
        """Write the content of a single file"""
        if self.single_file and self.selected_file and file_path == self.selected_file:
            f.write(f"\n### `{rel_path}` ⭐ (Selected file)\n")
        else:
            f.write(f"\n### `{rel_path}`\n")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                if len(content) > max_chars:
                    content = content[:max_chars] + f"\n\n// ... (content truncated, {len(file.read())} total characters)"

                # Detect language for syntax highlighting
                extension = file_path.suffix.lower()
                language_map = {
                    ".py": "python",
                    ".js": "javascript",
                    ".jsx": "javascript",
                    ".ts": "typescript",
                    ".tsx": "typescript",
                    ".cpp": "cpp",
                    ".cc": "cpp",
                    ".cxx": "cpp",
                    ".c": "c",
                    ".h": "c",
                    ".hpp": "cpp",
                    ".hxx": "cpp",
                    ".css": "css",
                    ".scss": "scss",
                    ".less": "less",
                    ".html": "html",
                    ".htm": "html",
                    ".xml": "xml",
                    ".json": "json",
                    ".yaml": "yaml",
                    ".yml": "yaml",
                    ".md": "markdown",
                    ".sql": "sql",
                    ".sh": "bash",
                    ".bat": "batch",
                    ".qml": "qml",
                    ".cmake": "cmake"
                }

                language = language_map.get(extension, "")
                f.write(f"```{language}\n{content}\n```\n")

        except Exception as e:
            f.write(f"```\n❌ Error reading file: {str(e)}\n```\n")

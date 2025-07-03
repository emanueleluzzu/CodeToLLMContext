import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, RichLog, Input, Button, Static, Checkbox
from textual.containers import Horizontal, Vertical
from textual import on, work
from code_context_generator import CodeContextGenerator

# Import settings, with fallback if file doesn't exist
try:
    from settings import skip_dirs, skip_files, allowed_extensions, max_file_size, css as get_css
except ImportError:
    def skip_dirs():
        return {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", ".vscode"}
    def skip_files():
        return {".gitignore", ".pyc", ".exe", ".dll", ".so", "settings.py"}
    def allowed_extensions():
        return {".cpp", ".h", ".py", ".js", ".md", ".txt", ".qml"}
    def max_file_size():
        return 5000
    def get_css():
        return ""

class CodeSharerApp(App):
    """App to generate code context with graphical interface"""

    TITLE = "Code Sharer - Context Generator"

    @property
    def CSS(self):
        """Dynamic CSS from settings"""
        custom_css = get_css()
        if custom_css:
            return custom_css
        # Fallback CSS if settings.py is not available
        return """
        Screen {
            layout: grid;
            grid-size: 2;
            grid-columns: 1fr 2fr;
            padding: 1;
        }
        #left-panel { width: 100%; height: 100%; }
        #tree-view { height: 65%; border: solid $accent; margin-bottom: 1; }
        #project-info { height: 35%; border: solid $primary; padding: 1; }
        #right-panel { width: 100%; height: 100%; }
        #code-view { height: 70%; border: solid $accent; overflow: auto; margin-bottom: 1; }
        #input-area { height: 30%; }
        #file-mode { margin-bottom: 1; }
        #prompt-input { margin-bottom: 1; }
        #buttons { layout: horizontal; height: 3; }
        Button { width: 1fr; margin: 0 1; }
        .success { color: $success; }
        .error { color: $error; }
        .warning { color: $warning; }
        .selected-file { color: $success; font-weight: bold; }
        """

    def __init__(self):
        super().__init__()
        self.current_path = Path.cwd()
        self.generator = None
        self.selected_file = None
        self.single_file_mode = False

    def compose(self) -> ComposeResult:
        """Compose the user interface"""
        with Vertical(id="left-panel"):
            yield DirectoryTree(str(self.current_path), id="tree-view")
            yield Static(self._get_project_info(), id="project-info")

        with Vertical(id="right-panel"):
            yield RichLog(id="code-view", highlight=True, markup=True)
            with Vertical(id="input-area"):
                yield Checkbox("📄 Single file mode", id="file-mode")
                yield Input(
                    placeholder="Enter your prompt/question and press Enter...",
                    id="prompt-input"
                )
                with Horizontal(id="buttons"):
                    yield Button("🚀 Generate [G]", id="generate-btn", variant="success")
                    yield Button("📁 Change Dir [C]", id="change-dir-btn", variant="primary")
                    yield Button("🗑️ Reset [R]", id="reset-btn", variant="warning")
                    yield Button("❌ Exit [ESC]", id="exit-btn", variant="error")

    def _get_project_info(self):
        """Generate project/file information"""
        info = f"📁 Project: {self.current_path.name}\n📍 Path: {self.current_path}\n"
        if self.single_file_mode and self.selected_file:
            info += f"📄 Selected file: {self.selected_file.name}\n🎯 Mode: Single file"
        else:
            info += "🎯 Mode: Complete project"
        return info

    def on_mount(self) -> None:
        """Initialization after mount"""
        self.query_one("#prompt-input").focus()
        log = self.query_one("#code-view")
        log.write("✅ [bold green]Code Sharer started![/bold green]")
        log.write(f"📁 Current directory: [bold]{self.current_path}[/bold]")
        log.write("💡 Enter a prompt and press Generate to create context")
        log.write("📄 Enable 'Single file mode' and select a file to process only one")
        log.write("⚡ Shortcuts: G=Generate, C=Change Directory, R=Reset, ESC=Exit")

    @on(DirectoryTree.DirectorySelected)
    def directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle directory selection"""
        self.current_path = Path(event.path)
        self.generator = None  # Reset generator
        self.selected_file = None  # Reset file selection
        self._update_project_info()

        log = self.query_one("#code-view")
        log.write(f"📂 [bold blue]Directory selected:[/bold blue] {self.current_path}")

    @on(DirectoryTree.FileSelected)
    def file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection"""
        selected_path = Path(event.path)
        log = self.query_one("#code-view")

        if self.single_file_mode:
            self.selected_file = selected_path
            self.current_path = selected_path.parent
            self.generator = None  # Reset generator
            self._update_project_info()
            log.write(f"📄 [bold green]File selected:[/bold green] {self.selected_file.name}")
            log.write(f"📂 Base directory: {self.current_path}")
        else:
            log.write(f"📄 [yellow]File clicked:[/yellow] {selected_path.name}")
            log.write("💡 Enable 'Single file mode' to select this file")

    @on(Checkbox.Changed, "#file-mode")
    def on_file_mode_changed(self, event: Checkbox.Changed) -> None:
        """Handle single file mode toggle"""
        self.single_file_mode = event.value
        log = self.query_one("#code-view")

        if self.single_file_mode:
            log.write("📄 [bold blue]Single file mode activated![/bold blue]")
            log.write("👆 Click on a file in the tree to select it")
            if self.selected_file:
                log.write(f"📄 Current file: [bold]{self.selected_file.name}[/bold]")
        else:
            log.write("📁 [bold blue]Complete project mode activated![/bold blue]")
            self.selected_file = None

        self._update_project_info()

    @on(Input.Submitted, "#prompt-input")
    def on_input_submitted(self) -> None:
        """Handle prompt submission"""
        self.generate_context()

    @on(Button.Pressed, "#generate-btn")
    def on_generate_pressed(self) -> None:
        """Handle generate button click"""
        self.generate_context()

    @on(Button.Pressed, "#change-dir-btn")
    def on_change_dir_pressed(self) -> None:
        """Handle directory change"""
        self.change_directory()

    @on(Button.Pressed, "#reset-btn")
    def on_reset_pressed(self) -> None:
        """Handle selections reset"""
        self.selected_file = None
        self.single_file_mode = False
        self.query_one("#file-mode").value = False
        self.generator = None
        self._update_project_info()

        log = self.query_one("#code-view")
        log.write("🔄 [bold yellow]Reset completed![/bold yellow]")
        log.write("📁 Complete project mode restored")

    @on(Button.Pressed, "#exit-btn")
    def on_exit_pressed(self) -> None:
        """Handle app exit"""
        self.exit()

    def _update_project_info(self):
        """Update project information"""
        info = self.query_one("#project-info")
        info.update(self._get_project_info())

    def change_directory(self):
        """Change working directory"""
        log = self.query_one("#code-view")
        log.write("📁 [bold blue]Select a new directory in the tree on the left[/bold blue]")

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts"""
        if event.key == "g":
            self.generate_context()
        elif event.key == "c":
            self.change_directory()
        elif event.key == "r":
            self.on_reset_pressed()
        elif event.key == "escape":
            self.exit()

    @work(exclusive=True)
    async def generate_context(self) -> None:
        """Generate context asynchronously"""
        prompt_input = self.query_one("#prompt-input")
        prompt = prompt_input.value.strip()

        if not prompt:
            log = self.query_one("#code-view")
            log.write("⚠️ [bold yellow]Enter a valid prompt![/bold yellow]")
            prompt_input.focus()
            return

        # Verify file selection in single mode
        if self.single_file_mode and not self.selected_file:
            log = self.query_one("#code-view")
            log.write("⚠️ [bold yellow]Select a file in single file mode![/bold yellow]")
            return

        log = self.query_one("#code-view")
        log.write(f"🔄 [bold blue]Generation in progress...[/bold blue]")
        log.write(f"💭 Prompt: [italic]{prompt}[/italic]")

        if self.single_file_mode and self.selected_file:
            log.write(f"📄 File: [bold green]{self.selected_file.name}[/bold green]")
        else:
            log.write(f"📁 Project: [bold blue]{self.current_path.name}[/bold blue]")

        try:
            # Initialize generator if needed
            if not self.generator:
                if self.single_file_mode and self.selected_file:
                    self.generator = CodeContextGenerator(str(self.selected_file))
                else:
                    self.generator = CodeContextGenerator(str(self.current_path))

            # Generate context
            await asyncio.to_thread(self._generate_sync, prompt)

            log.write("✅ [bold green]Context generated successfully![/bold green]")
            log.write("📋 [blue]Copy the content from context.md and paste it in the chat![/blue]")

        except Exception as e:
            log.write(f"❌ [bold red]Error during generation:[/bold red] {str(e)}")

        # Clear prompt
        prompt_input.value = ""
        prompt_input.focus()

    def _generate_sync(self, prompt):
        """Synchronous generation function"""
        # Create context with the prompt
        self.generator.generate_context_with_prompt(prompt)


if __name__ == "__main__":
    app = CodeSharerApp()
    app.run()

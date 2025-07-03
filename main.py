#!/usr/bin/env python3
import sys
import argparse
from gui import CodeSharerApp
from code_context_generator import CodeContextGenerator

def main():
    if "--gui" in sys.argv:
        app = CodeSharerApp()
        app.run()
    else:
        parser = argparse.ArgumentParser(description="Generate project context for chat")
        parser.add_argument("path", nargs="?", help="Project path or single file (default: current)")
        parser.add_argument("--max-chars", type=int, default=5000, help="Character limit per file")
        parser.add_argument("--output", default="context.md", help="Output file")
        parser.add_argument("--gui", action="store_true", help="Launch graphical interface")
        parser.add_argument("--file", action="store_true", help="The path is a single file")

        args = parser.parse_args()

        if args.gui:
            app = CodeSharerApp()
            app.run()
        else:
            generator = CodeContextGenerator(args.path, single_file=args.file)
            generator.generate_context(output_file=args.output, max_chars=args.max_chars)


if __name__ == "__main__":
    main()

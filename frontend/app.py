"""
Main Entry Point for the Sign Language Translator Frontend GUI.
Launches the CustomTkinter desktop interface.
"""

import sys
from pathlib import Path

# Ensure the project root and frontend directories are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from frontend.ui.main_window import MainWindow


def main():
    """Start the Sign Language Translator GUI application."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

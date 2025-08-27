#!/usr/bin/env python3
"""
Advanced Steganography Suite - Main Entry Point
Supports CLI, GUI and Web interfaces
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Advanced Steganography Suite")
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    parser.add_argument('--web', action='store_true', help='Launch Web interface (Flask app)')
    
    args = parser.parse_args()
    
    if args.web:
        # Import flask app and run web interface
        from cli.main_cli import main as cli_main
        from gui.main_window import run_gui # Replace 'app' with your flask app module filename
        print("Launching Web Interface...")
        cli_main.run(host='0.0.0.0', port=5000, debug=True)
    elif args.gui or len(sys.argv) == 1:
        # Launch GUI if --gui specified or no arguments
        from gui.main_window import run_gui
        print("Launching Graphical Interface...")
        run_gui()
    else:
        # Launch CLI otherwise
        from cli.main_cli import main as cli_main
        cli_main()

if __name__ == '__main__':
    main()

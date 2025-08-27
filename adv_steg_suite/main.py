#!/usr/bin/env python3
"""
Advanced Steganography Suite - Main Entry Point
"""
import argparse
import sys
from cli.main_cli import main as cli_main
from gui.main_window import run_gui

def main():
    parser = argparse.ArgumentParser(description="Advanced Steganography Suite")
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    
    args = parser.parse_args()
    
    if args.gui or len(sys.argv) == 1:
        print("Launching Graphical Interface...")
        run_gui()
    else:
        cli_main()

if __name__ == '__main__':
    main()
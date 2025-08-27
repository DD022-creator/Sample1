#!/usr/bin/env python3
"""
Web application launcher - Run this from the root directory
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import the app
from web_app.app import app

if __name__ == '__main__':
    print("🚀 Starting Advanced Steganography Web Suite...")
    print("🌐 Open: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
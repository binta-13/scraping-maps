"""
Netlify Function entry point - __main__.py
"""
import sys
import os

# Tambahkan path ke parent directory untuk import server.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import handler dari server.py di parent directory
from server import handler


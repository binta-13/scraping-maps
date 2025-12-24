"""
Netlify serverless function untuk Flask app
"""
import sys
import os

# Tambahkan path ke root project
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_path)

# Set working directory
os.chdir(root_path)

from serverless_wsgi import handle_request
from app import app

def handler(event, context):
    """Handler untuk Netlify Functions"""
    try:
        return handle_request(app, event, context)
    except Exception as e:
        # Error handling untuk debugging
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': str(e)
        }


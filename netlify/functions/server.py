"""
Netlify serverless function untuk Flask app
"""
import sys
import os
import json

# Tambahkan path ke root project
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_path)

# Set working directory
os.chdir(root_path)

try:
    from serverless_wsgi import handle_request
    from app import app
    
    def handler(event, context):
        """Handler untuk Netlify Functions"""
        try:
            # Handle request menggunakan serverless-wsgi
            response = handle_request(app, event, context)
            return response
        except Exception as e:
            # Error handling untuk debugging
            import traceback
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            print(f"Error in handler: {error_msg}")
            print(traceback_str)
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': error_msg,
                    'traceback': traceback_str
                })
            }
except ImportError as e:
    # Fallback jika import gagal
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': f'Import error: {str(e)}',
                'message': 'Failed to import Flask app or serverless-wsgi'
            })
        }


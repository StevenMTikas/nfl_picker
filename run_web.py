#!/usr/bin/env python3
"""
Run the NFL Picker web application.
"""

import os
import sys

# Set environment variables if not set
if not os.getenv('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'

if not os.getenv('PORT'):
    os.environ['PORT'] = '5000'

# Import and run the app
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    print(f"Starting NFL Picker web app on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


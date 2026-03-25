import sys
import os

# Ensure the root directory is in the Python path so 'backend' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# This 'app' object is what Vercel needs to handle the HTTP requests
handler = app

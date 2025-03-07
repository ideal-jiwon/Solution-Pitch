#!/bin/bash

# Move into the backend directory
cd backend

# Install dependencies (if not installed)
pip install -r requirements.txt

# Run Flask app using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 server:app

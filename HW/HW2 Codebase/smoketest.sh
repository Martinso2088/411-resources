#!/bin/bash
set -e

# Start the Flask app (adjust if your entry point is different)
echo "Starting Flask app..."
FLASK_APP=boxing.app flask run &

FLASK_PID=$!
sleep 3

# Make a test request
echo "Testing Flask endpoint..."
curl -s http://localhost:5000/health || echo "Health endpoint not found"

# Kill Flask app
kill $FLASK_PID

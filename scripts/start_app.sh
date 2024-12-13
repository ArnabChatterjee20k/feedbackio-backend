# !/bin/bash
./scripts/kill_gunicorn.sh
echo "Starting 4 workers of the app"
gunicorn -w 4 -b 0.0.0.0 "main:app"
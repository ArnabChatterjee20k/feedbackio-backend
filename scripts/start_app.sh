# !/bin/bash
./scripts/kill_gunicorn.sh
# echo "Starting 4 workers of the app"
# gunicorn -w 1 --threads 5 -b 0.0.0.0 "main:app"
gunicorn -w 1 -k uvicorn.workers.UvicornWorker --threads 4 --bind 0.0.0.0:5000 main:app

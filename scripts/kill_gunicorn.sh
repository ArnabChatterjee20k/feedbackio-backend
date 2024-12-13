# !/bin/bash
pids=$(lsof -t -i :8000)
if [ -n "$pids" ]; then
  echo -e "Killing PIDs:\n$pids"
  kill -9 $pids
else
  echo "No processes found using port 8000."
fi
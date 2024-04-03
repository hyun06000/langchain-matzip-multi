uvicorn blog_expert:app --reload --port 8001 &
uvicorn map_expert:app --reload --port 8002 &
uvicorn translation_expert:app --reload --port 8003 &
sleep 3

python supervisor.py

#clear
PIDS=$(pgrep -f uvicorn)

echo "killing uvicorn process: $PIDS"
for PID in $PIDS
do
kill $PID
done

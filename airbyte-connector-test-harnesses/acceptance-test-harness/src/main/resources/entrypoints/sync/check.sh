trap "touch TERMINATION_FILE_CHECK" EXIT
(set -e; while true; do curl -s HEARTBEAT_URL &> /dev/null; sleep 1; done) &
CHILD_PID=$!
(while true; do if [ -f TERMINATION_FILE_MAIN ]; then kill $CHILD_PID; exit 0; fi; sleep 1; done) &
wait $CHILD_PID
EXIT_CODE=$?

if [ -f TERMINATION_FILE_MAIN ]
then
  exit 0
else
  exit $EXIT_CODE
fi

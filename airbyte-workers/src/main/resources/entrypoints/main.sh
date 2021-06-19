trap "touch TERMINATION_FILE_MAIN" EXIT
(OPTIONAL_STDIN (ENTRYPOINT) 2> STDERR_PIPE_FILE > STDOUT_PIPE_FILE) &
CHILD_PID=$!
(while true; do if [ -f TERMINATION_FILE_CHECK ]; then echo "Heartbeat to worker failed, exiting..."; exit 1; fi; sleep 1; done) &
wait $CHILD_PID
exit $?

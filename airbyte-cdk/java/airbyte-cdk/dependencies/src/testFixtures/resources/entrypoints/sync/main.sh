trap "touch TERMINATION_FILE_MAIN" EXIT
trap "echo 'received ABRT'; exit 1;" ABRT

ENTRYPOINT_OVERRIDE=ENTRYPOINT_OVERRIDE_VALUE

if [ ! -z "$ENTRYPOINT_OVERRIDE" ]; then
  echo "Overriding AIRBYTE_ENTRYPOINT to: $ENTRYPOINT_OVERRIDE"
  AIRBYTE_ENTRYPOINT=$ENTRYPOINT_OVERRIDE
elif [ -z "$AIRBYTE_ENTRYPOINT" ]; then
  echo "Entrypoint was not set! AIRBYTE_ENTRYPOINT must be set in the container to run on Kubernetes." >> STDERR_PIPE_FILE
  exit 127
else
  echo "Using existing AIRBYTE_ENTRYPOINT: $AIRBYTE_ENTRYPOINT"
fi

((eval "$AIRBYTE_ENTRYPOINT ARGS" 2> STDERR_PIPE_FILE > STDOUT_PIPE_FILE) OPTIONAL_STDIN) &
CHILD_PID=$!

# Check for TERMINATION_FILE_CHECK in a loop to handle heartbeat failure
(
  # must use $$$$ instead of $$ because kube entrypoint transforms $$ into $
  # see https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/#entrypoint for explanation
  PARENT_PID=$$$$
  echo "PARENT_PID: ${PARENT_PID}"
  while true
  do
    if [ -f TERMINATION_FILE_CHECK ]
    then
      echo "Heartbeat to worker failed, exiting..."
      kill -s ABRT ${PARENT_PID}
      exit 0
    fi
    sleep 1
  done
) &

echo "Waiting on CHILD_PID $CHILD_PID"
wait $CHILD_PID
EXIT_STATUS=$?
echo "EXIT_STATUS: $EXIT_STATUS"
exit $EXIT_STATUS

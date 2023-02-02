USES_STDIN=USES_STDIN_VALUE

mkfifo STDOUT_PIPE_FILE_VALUE
mkfifo STDERR_PIPE_FILE_VALUE

if [ "$USES_STDIN" = true ]; then
  mkfifo STDIN_PIPE_FILE_VALUE
fi

ITERATION=0
MAX_ITERATION=MAX_ITERATION_VALUE
DISK_USAGE=$(du -s /config | awk '{print $1;}')

until [ -f SUCCESS_FILE_NAME_VALUE -o $ITERATION -ge $MAX_ITERATION ]; do
  ITERATION=$((ITERATION+1))
  LAST_DISK_USAGE=$DISK_USAGE
  DISK_USAGE=$(du -s /config | awk '{print $1;}')
  if [ $DISK_USAGE -gt $LAST_DISK_USAGE ]; then
    ITERATION=0
  fi
  sleep SLEEP_PERIOD_VALUE
done

if [ -f SUCCESS_FILE_NAME_VALUE ]; then
  echo "All files copied successfully, exiting with code 0..."
  exit 0
else
  echo "Timeout while attempting to copy to init container, exiting with code 1..."
  exit 1
fi

#!/bin/bash

if [ $# != 3 ]; then
 echo "please set a path of main file, a path of config file and a stream name"
 exit 1
fi

MAIN_FILE=$1
CONFIG_PATH=$2
STREAM_NAME=$3
TMP_FILE=/tmp/${STREAM_NAME}_config.json
TMP_STATE_FILE=/tmp/${STREAM_NAME}_stage.json
TMP_STATE_FILE2=/tmp/${STREAM_NAME}_stage2.json
PYTHON=python

cmd="${PYTHON} ${MAIN_FILE} discover --config ${CONFIG_PATH}"
echo "$cmd"
cmd="$cmd | jq -c '.catalog.streams | map(select(.name ==\"${STREAM_NAME}\")) | .[] |= . + {stream: .} | map({stream}) | map(. + {\"sync_mode\": \"incremental\", \"destination_sync_mode\": \"append\"}) | {streams: .}'"
echo "$cmd"
cmd="$cmd > $TMP_FILE || exit 1"
echo "$cmd"
bash -c "$cmd"

cmd="${PYTHON} ${MAIN_FILE} read --config ${CONFIG_PATH} --catalog ${TMP_FILE}"
echo "$cmd"
cat_cmd="$cmd | tee $TMP_STATE_FILE2 || exit 1"
echo "$cat_cmd"
bash -c "$cat_cmd"

echo "TRY WITH SAVED STATE"
cmd2="cat $TMP_STATE_FILE2 | grep \"STATE\" | head -n1 | jq -c '.state.data' | tee ${TMP_STATE_FILE} || exit 1"
echo "$cmd2"
bash -c "$cmd2"
state_cmd="$cmd --state ${TMP_STATE_FILE} || exit 1"
echo "$state_cmd"
bash -c "$state_cmd"
echo "FINISHED"
exit 0

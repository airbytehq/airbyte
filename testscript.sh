mkdir -p kind_logs
echo "Loading images into KIND..."
echo "test string "> kind_logs/server &
process_ids=$!
sleep 5 && echo "test string "> kind_logs/webapp &
process_ids="$! $process_ids"
sleep 20 > kind_logs/worker &
process_ids="$! $process_ids"
echo "test string "> kind_logs/db &
process_ids="$! $process_ids"
echo "test string "> kind_logs/container &
process_ids="$! $process_ids"
echo "test string "> kind_logs/bootloader &
process_ids="$! $process_ids"
tail -f kind_logs/* &
tail_id=$!
echo "\\n\\n\\n Waiting for the follows process IDs to finish $process_ids"
wait $process_ids && kill $tail_id

while [ 1 ]; do
    clear;
echo "With errors:"
grep -riL "7 passed" log-source* | wc -l
grep -riL "7 passed" log-source* | tail -5

echo "\n\n\n"
echo "Success:"
grep -ril "7 passed" log-source* | wc -l
grep -ril "7 passed" log-source* | tail -5
sleep 1 ;done
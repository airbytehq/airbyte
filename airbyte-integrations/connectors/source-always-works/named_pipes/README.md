Try to use a mounted named pipe instead of using socat.
```
mkdir /tmp/np_file 
docker run -it --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_source:dev -c "mkfifo /tmp/np_file/pipe && /tmp/run.sh > /tmp/np_file/pipe && rm /tmp/np_file/pipe" | docker run -i --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_dest:dev -c "tail -f /tmp/np_file/pipe | /tmp/run.sh"
```


docker run -it --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_source:dev -c "rm /tmp/np_file/pipe && mkfifo /tmp/np_file/pipe && /tmp/run.sh > /tmp/np_file/pipe" | docker run -i --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_dest:dev -c "tail -f /tmp/np_file/pipe | /tmp/run.sh"
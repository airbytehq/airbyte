Try to use a mounted named pipe instead of using socat.

For builds:
```
cd ~/code/airbyte/airbyte-integrations/connectors/source-always-works/named_pipes/np_source
docker build -t np_source:dev .
cd ~/code/airbyte/airbyte-integrations/connectors/source-always-works/named_pipes/np_dest
docker build -t np_dest:dev .
```

Then run the "init container" equivalent:
```
docker run -it --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_source:dev -c "rm /tmp/np_file/pipe && mkfifo /tmp/np_file/pipe" 
```

Then run the source and destination at the same time (you can do either first):
```
docker run -it --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_source:dev -c "/tmp/run.sh > /tmp/np_file/pipe" 
docker run -it --rm -v /tmp/np_file:/tmp/np_file --entrypoint "sh" np_dest:dev -c "cat /tmp/np_file/pipe | /tmp/run.sh"
```

Notes:
- The source blocks until something starts reading from the named pipe.
- `cat` detects when the source reaches its EOF
- You can start the destination before the source and it terminates as expected.

Todo:
- Set this up for Kube
- Use an init container to create the initial named pipe
- Use a shared mount

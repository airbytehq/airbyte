# Kube Queueing POC

To build sync worker:
```
cd ~/code/airbyte
./gradlew :airbyte-workers:airbyteDocker
cd ~/code/airbyte/airbyte-workers/docker-shim-mvp/destination-listen-and-echo
docker build -t airbyte/destination-listen-and-echo:dev .
```

To run the sync worker
```
cd ~/code/airbyte/airbyte-workers/src/main/resources/kube_queue_poc
kubectl apply -f kube-sync-workers.yaml
```

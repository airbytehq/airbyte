# Local JSON

:::danger

This destination is meant to be used on a local workstation and won't work on Kubernetes production deployments. This is because the destination writes data to the local filesystem of the container, which is not accessible outside the pod in a Kubernetes environment unless you configure persistent volumes.

:::

## Overview

This destination writes data to a directory on the filesystem within the Airbyte container. All data is written under the `/local` directory inside the container.

### Sync Overview

#### Output schema

Each stream will be output into its own file. Each file will a collections of `json` objects containing 3 fields:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the extracted data.

#### Features

| Feature                        | Supported |     |
| :----------------------------- | :-------- | :-- |
| Full Refresh Sync              | Yes       |     |
| Incremental - Append Sync      | Yes       |     |
| Incremental - Append + Deduped | No        |     |
| Namespaces                     | No        |     |

#### Performance considerations

This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

The `destination_path` will always start with `/local` whether it is specified by the user or not. Any directory nesting within local will be mapped onto the local mount.

The connector code enforces that all paths must be under the `/local` directory. If you provide a path that doesn't start with `/local`, it will be automatically prefixed with `/local`. Attempting to write to a location outside the `/local` directory will result in an error.

:::caution

When using abctl to deploy Airbyte locally, the data is stored within the Kubernetes cluster created by abctl. You'll need to use kubectl commands to access the data as described in the "Access Replicated Data Files" section below.

:::

### Example:

- If `destination_path` is set to `/local/cars/models`
- then all data will be written to `/local/cars/models` directory inside the container

:::info
**Understanding Airbyte's Architecture:** In Airbyte's Kubernetes deployment, destination connectors don't run as standalone pods. Instead, they are executed as jobs by the worker pods. This means that to persist data from the Local JSON destination, you must mount volumes to the worker pods, not to the destination connectors directly.
:::

## Using with Kubernetes

When using Airbyte in a Kubernetes environment, you need to follow these steps to properly configure and access data:

1. **Create a Persistent Volume**
   - First, create a persistent volume claim (PVC) in your Kubernetes cluster:
     ```
     kubectl apply -f - <<EOF
     apiVersion: v1
     kind: PersistentVolumeClaim
     metadata:
       name: local-json-data
     spec:
       accessModes:
         - ReadWriteOnce
       resources:
         requests:
           storage: 1Gi
     EOF
     ```
   - Note: Adjust the namespace and other parameters according to your Kubernetes setup

2. **Configure the Destination with Volume Mount**
   - When setting up your Local JSON destination, set the destination path to `/local/data`
   - In the Airbyte UI, create or edit your connection to use this destination
   - **Important**: You must configure the worker pods that run the destination connector to mount the PVC during sync
   - In Airbyte's Kubernetes deployment, destination connectors run as jobs launched by the worker deployment
   - For Helm deployments, modify your values.yaml to include volume mounts for the worker:
     ```yaml
     worker:
       extraVolumes:
         - name: data-volume
           persistentVolumeClaim:
             claimName: local-json-data
       extraVolumeMounts:
         - name: data-volume
           mountPath: /local
     ```
   - Apply this configuration when installing or upgrading Airbyte:
     ```bash
     helm upgrade --install airbyte airbyte/airbyte -n airbyte -f values.yaml
     ```
   - For manual Kubernetes deployments, patch the worker deployment:
     ```bash
     kubectl patch deployment airbyte-worker -n airbyte --patch '
     {
       "spec": {
         "template": {
           "spec": {
             "volumes": [
               {
                 "name": "data-volume",
                 "persistentVolumeClaim": {
                   "claimName": "local-json-data"
                 }
               }
             ],
             "containers": [
               {
                 "name": "airbyte-worker",
                 "volumeMounts": [
                   {
                     "name": "data-volume",
                     "mountPath": "/local"
                   }
                 ]
               }
             ]
           }
         }
       }
     }'
     ```
   - This step is critical - without mounting the volume to the worker pods that run the destination, data will not persist

3. **Access Data After Sync Completion**
   - For completed pods where the data is stored in the persistent volume, create a temporary pod with the volume mounted:
     ```
     kubectl apply -f - <<EOF
     apiVersion: v1
     kind: Pod
     metadata:
       name: file-access
     spec:
       containers:
       - name: file-access
         image: busybox
         command: ["sh", "-c", "ls -la /data && sleep 3600"]
         volumeMounts:
         - name: data-volume
           mountPath: /data
       volumes:
       - name: data-volume
         persistentVolumeClaim:
           claimName: local-json-data
     EOF
     ```
   - Then access the pod to view files:
     ```
     kubectl exec -it file-access -- sh
     ```
   - To view file contents directly:
     ```
     # First, list all directories to find your stream names
     kubectl exec -it file-access -- ls -la /data
     
     # Then view specific files (replace stream_name with actual stream name from above)
     kubectl exec -it file-access -- cat /data/stream_name/*.jsonl
     ```
   - When finished, delete the temporary pod:
     ```
     kubectl delete pod file-access
     ```

4. **Alternative: View File Paths in Logs**
   - If you can't mount the volume, you can at least see the file paths in the logs:
     ```
     kubectl logs <pod-name> | grep "File output:"
     ```

Note: The exact pod name will depend on your specific connection ID and sync attempt. Look for pods with names containing "destination" and your connection ID.

If you are running Airbyte on Windows, you may need to adjust these commands accordingly. You can also refer to the [alternative file access methods](/integrations/locating-files-local-destination.md) for other approaches.

## Troubleshooting

### Verifying Volume Mounts

If you're having trouble with data persistence, follow these steps to verify your volume mounting configuration:

1. **Check if the PVC was created successfully:**
   ```bash
   kubectl get pvc local-json-data -n <your-namespace>
   ```
   The status should be "Bound".

2. **Verify that the worker pods have the volume mounted:**
   ```bash
   kubectl describe pod -l app=airbyte-worker -n <your-namespace> | grep -A 10 "Volumes:"
   ```
   You should see your volume listed with the correct PVC.

3. **Check the logs of a recent sync job for file paths:**
   ```bash
   kubectl logs <destination-pod-name> -n <your-namespace> | grep "File output:"
   ```
   This should show paths starting with `/local/`.

4. **Common issues:**
   - Volume not mounted to worker pods (most common issue)
   - Incorrect mount path (must be `/local`)
   - PVC not bound or available
   - Insufficient permissions on the mounted volume

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------- |
| 0.2.12 | 2024-12-18 | [49908](https://github.com/airbytehq/airbyte/pull/49908) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.2.11 | 2022-02-14 | [14641](https://github.com/airbytehq/airbyte/pull/14641) | Include lifecycle management |

</details>

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

## Using with Kubernetes (abctl)

Since Airbyte runs in a Kubernetes cluster managed by abctl, you need to follow these steps to properly configure and access data:

1. **Create a Persistent Volume**
   - First, create a persistent volume claim (PVC) in your Kubernetes cluster:
     ```
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl apply -f - <<EOF
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

2. **Configure the Destination with Volume Mount**
   - When setting up your Local JSON destination, set the destination path to `/local/data`
   - In the Airbyte UI, create or edit your connection to use this destination
   - **Important**: You must configure the destination pods to mount the PVC during sync:
     ```
     # First, find the destination pods for your connection
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods | grep destination
     
     # Then, create a custom resource to mount the volume for future destination pods
     # Note: The exact implementation will depend on your Airbyte deployment configuration
     # Consult the Airbyte documentation for your specific deployment method
     ```
   - This step is critical - without mounting the volume to the destination pod during sync, data will not persist

3. **Access Data After Sync Completion**
   - For completed pods where the data is stored in the persistent volume, create a temporary pod with the volume mounted:
     ```
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl apply -f - <<EOF
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
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl exec -it file-access -- sh
     ```
   - To view file contents directly:
     ```
     # First, list all directories to find your stream names
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl exec -it file-access -- ls -la /data
     
     # Then view specific files (replace stream_name with actual stream name from above)
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl exec -it file-access -- cat /data/stream_name/*.jsonl
     ```
   - When finished, delete the temporary pod:
     ```
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl delete pod file-access
     ```

4. **Alternative: View File Paths in Logs**
   - If you can't mount the volume, you can at least see the file paths in the logs:
     ```
     kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <pod-name> | grep "File output:"
     ```

Note: The exact pod name will depend on your specific connection ID and sync attempt. Look for pods with names containing "destination" and your connection ID.

If you are running Airbyte on Windows, you may need to adjust these commands accordingly. You can also refer to the [alternative file access methods](/integrations/locating-files-local-destination.md) for other approaches.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------- |
| 0.2.12 | 2024-12-18 | [49908](https://github.com/airbytehq/airbyte/pull/49908) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.2.11 | 2022-02-14 | [14641](https://github.com/airbytehq/airbyte/pull/14641) | Include lifecycle management |

</details>

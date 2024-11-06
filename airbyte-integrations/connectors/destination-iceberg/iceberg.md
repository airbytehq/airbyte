# Custom Iceberg Catalog Demo

## Setup

### Minio

The demo uses Minio as the storage location.  If you have Airbyte cloud deployed locally, follow these steps:

1. Expose the Minio UI by editing the `airbyte-minio` deployment:
```shell
> kubectl edit deployment -n ab airbyte-minio

# add the following env vars
        - name: MINIO_ROOT_USER
          value: minio
        - name: MINIO_ROOT_PASSWORD
          value: minio123
        - name: MINIO_CONSOLE_ADDRESS
          value: :9001
          
# expose the following port
          
        - containerPort: 9001
          protocol: TCP
```
2. Establish two port-forwards to the Minio pod:
```shell
> kubectl port-forward deployment/airbyte-minio -n ab 9000:9000
> kubectl port-forward deployment/airbyte-minio -n ab 9001:9001
```

3. Open a browser window and navigate to http://localhost:9001/.  Use the root user name/password from the env vars to log in.

## Running

To run the demo, create/edit a new run profile in Intellij:

* Main Class:  `io.airbyte.integrations.destination.iceberg.IcebergTestKt`
* Program arguments `http://localhost:9000 minio minio123`

Execute the application to create files.
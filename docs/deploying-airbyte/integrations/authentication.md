---
products: oss-community, oss-enterprise
---

# Authentication

Airbyte comes with built in authentication based on the email provided at setup and a generated password. If you need to
view your password and you are running Airbyte through `abctl` you can run the following:

```shell
abctl local credentials
```
Which should output something similar to:

```shell
{
  "password": "password",
  "client-id": "client_id",
  "client-secret": "client_secret"
}
```

If you have deployed to your own Kubernetes cluster using Helm, then you can view your credentials by running the 
following:

```shell
kubectl get secret airbyte-auth-secrets -n <YOUR_NAMESPACE> -o yaml
```

Which will return something similar to:

```shell
apiVersion: v1
data:
  instance-admin-client-id: Y2Q1ZTc4ZWEtMzkwNy00ZThmLWE1ZWMtMjIyNGVhZTFiYzcw
  instance-admin-client-secret: cmhvQkhCODlMRmh1REdXMWt3REpHZTJMaUd3N3c2MjU=
  instance-admin-password: d0V2bklvZEo1QUNHQnpPRWxrOWNSeHdFUGpJMWVzMWg=
kind: Secret
metadata:
  creationTimestamp: "2024-07-31T04:22:54Z"
  name: airbyte-auth-secrets
  namespace: airbyte-abctl
  resourceVersion: "600"
  uid: f47170eb-f739-4e58-9013-b7afb3ac336a
type: Opaque
```

These values are base64 encoded, to decode your password run the following:

```shell
echo 'cmhvQkhCODlMRmh1REdXMWt3REpHZTJMaUd3N3c2MjU=' | base64 -d
```

## Turning Off Authentication

There may be times when your wish to turn off authentication, for instance if you have already configured a proxy that 
authenticates users with your organization's SSO. In these cases you can turn off Airbyte's authentication by adding the 
following to your values.yaml file:

```yaml
global:
  auth:
    enabled: false
```

For users that are using the `abctl` tool you can apply this by running the following:

```shell
abctl local install --values ./values.yaml
```

## Setting a Password via Secrets

You can also control the default password by supplying your own values as a Kubernetes secret. The following show the 
Secret name and fields that should be added to a file called `secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-auth-secrets
type: Opaque
stringData:
  instance-admin-password: # password

  # Override these if you want to access the API with known credentials
  #instance-admin-client-id: # my-client-id
  #instance-admin-client-secret: # my-client-secret
```

If you are deploying Airbyte with `abctl` you can run:

```shell
abctl local install --secret secret.yaml
```

If you are deploying to your own Kubernetes cluster, run:

```shell
kubectl apply -f secret.yaml -n <YOUR_NAMESPACE>
```

You may need to restart the airbyte-server pod for the changes to take effect.
# Run Airbyte Locally from Kubernetes

All commands should be run from the root Airbyte source directory.

1. Make sure you are using the correct Kubernetes context with `kubectl config current-context`
1. Apply the manifests for one of:
    * Latest stable version
        1. Apply with `kubectl apply -k kube/overlays/stable`
    * If you want to use the latest development version:
        1. Build the `dev` version of images with `./gradlew composeBuild`
        1. Apply with `kubectl apply -k kube/overlays/dev`
1. Wait for pods to be "Running" on `kubectl get pods | grep airbyte`
1. Run `kubectl port-forward svc/airbyte-server-svc 8001:8001` in a new terminal window.
    * This exposes `airbyte-server`, the Airbyte api server.
    * If you redeploy `airbyte-server`, you will need to re-run this process.
1. Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80` in a new terminal window.
    * This exposes `airbyte-webapp`, the server for the static web app.
    * These static assets will make calls to the Airbyte api server, which is why both services needed to be port forwarded.
    * If you redeploy `airbyte-webapp`, you will need to re-run this process.
1. Go to http://localhost:8000/ and use Airbyte!

## Operating Airbyte on Kubernetes

### Kustomize

We use [Kustomize](https://kustomize.io/), which is built into `kubectl` to allow overrides for different environments.

Our shared resources are in the `kube/resources` directory, and we define overlays for each environment. We recommend creating your own overlay if you want to customize your deployments. 

Example `kustomization.yaml` file:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - https://github.com/airbytehq/airbyte.git/kube/overlays/stable?ref=master
```

This would allow you to define custom resources or extend existing resources, even within your own VCS.

### View Raw Manifests

For a specific overlay, you can run `kubectl kustomize kube/overlays/dev` to view the manifests that Kustomize will apply to your Kubernetes cluster. This is useful for debugging because it will show the exact resources you are defining.

### Resizing Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported for your type of mount. For a production instance, it's useful to track the usage of volumes to ensure they don't run out of space.

### Copy Files To/From Volumes

See the documentation for [`kubectl cp`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp).

### Iterating

If you're developing using a local context and are not using your local Kubernetes instance for anything else, you can iterate with the following series of commands. 
```
./gradlew composeBuild # build dev images
kubectl delete "$(kubectl api-resources --namespaced=true --verbs=delete -o name | tr "\n" "," | sed -e 's/,$//')" --all # DELETES ALL RESOURCES. DO NOT USE ON CLUSTERS RUNNING MORE THAN AIRBYTE!
kubectl apply -k kube/overlays/dev # applies manifests
```

Then restart the port-forwarding commands.

### Listing Files

```
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx ls /tmp/workspace/8
```

### Reading Files

```
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx cat /tmp/workspace/8/0/logs.log
```

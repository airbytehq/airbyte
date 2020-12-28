# Kubernetes

## Support
This is an early proof of concept for Kubernetes support. It has been tested on:
* Local single-node Kube clusters (docker-desktop for Mac)
* Google Kubernetes Engine (GKE)

Please let us know on Slack or with a Github Issue if you're having trouble running it on these or other platforms. We'll be glad to help you get it running.

## Launching

All commands should be run from the root Airbyte source directory.

1. Make sure you are using the correct Kubernetes context with `kubectl config current-context`
2. Apply the manifests for one of:
    * Latest stable version
        1. Apply with `kubectl apply -k kube/overlays/stable`
3. Wait for pods to be "Running" on `kubectl get pods | grep airbyte`
4. Run `kubectl port-forward svc/airbyte-server-svc 8001:8001` in a new terminal window.
    * This exposes `airbyte-server`, the Airbyte api server.
    * If you redeploy `airbyte-server`, you will need to re-run this process.
5. Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80` in a new terminal window.
    * This exposes `airbyte-webapp`, the server for the static web app.
    * These static assets will make calls to the Airbyte api server, which is why both services needed to be port forwarded.
    * If you redeploy `airbyte-webapp`, you will need to re-run this process.
6. Go to http://localhost:8000/ and use Airbyte!

## Current Limitations

* The server, scheduler, and workers must all run on the same node in the Kubernetes cluster.
* Airbyte passes messages inefficiently between pods by `kubectl attach`-ing to pods using `kubectl run`.
* The provided manifests do not easily allow configuring a non-default namespace.
* Latency for UI operations is high.
* We don't clean up completed worker job and pod histories. They require manual deletion.
* Please let us know on Slack:
    * if those issues are blocking your adoption of Airbyte.
    * if you encounter any other issues or limitations of our Kube implementation.
    * if you'd like to make contributions to fix some of these issues!

## Kustomize

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

## View Raw Manifests

For a specific overlay, you can run `kubectl kustomize kube/overlays/dev` to view the manifests that Kustomize will apply to your Kubernetes cluster. This is useful for debugging because it will show the exact resources you are defining.

## Resizing Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported for your type of mount. For a production instance, it's useful to track the usage of volumes to ensure they don't run out of space.

## Copy Files To/From Volumes

See the documentation for [`kubectl cp`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp).

## Dev Iteration (on local Kubernetes clusters)

If you're developing using a local context and are not using your local Kubernetes instance for anything else, you can iterate with the following series of commands. 
```
./gradlew composeBuild # build dev images
kubectl delete -k kube/overlays/dev # optional, if you want to try recreating resources
kubectl apply -k kube/overlays/dev # applies manifests
```

Then restart the port-forwarding commands.

Note: this does not remove jobs and pods created for Airbyte workers.

If you are in a dev environment on a local cluster only running Airbyte and want to start completely from scratch, you can use the following command to destroy everything on the cluster:
```
# BE CAREFUL, THIS COMMAND DELETES ALL RESOURCES, EVEN NON-AIRBYTE ONES!
kubectl delete "$(kubectl api-resources --namespaced=true --verbs=delete -o name | tr "\n" "," | sed -e 's/,$//')" --all
```

## Dev Iteration (on GKE)

The process is similar to developing on a local cluster, except you will need to build the local version and push it to 
your own container registry with names such as `your-registry/scheduler`. Then you will need to configure an overlay to override
the name of images and apply your overlay with `kubectl apply -k <path to your overlay`.

## Listing Files

```
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx ls /tmp/workspace/8
```

## Reading Files

```
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx cat /tmp/workspace/8/0/logs.log
```

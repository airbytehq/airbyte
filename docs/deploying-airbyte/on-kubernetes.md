# On Kubernetes

> :warning: **Alpha Preview**: This is an early preview of Kubernetes that is pinned to Airbyte version 0.16.1. We do not recommend this preview for production use.

## Support

This is an early preview of Kubernetes support. It has been tested on:

* Local single-node Kube clusters \(docker-desktop for Mac\)
* Google Kubernetes Engine \(GKE\)
* Amazon Elastic Kubernetes Service \(EKS\)

Please let us know on [Slack](https://slack.airbyte.io) or with a Github Issue if you're having trouble running it on these or other platforms. We'll be glad to help you get it running.

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
6. Go to [http://localhost:8000/](http://localhost:8000/) and use Airbyte!

## Current Limitations

* The server, scheduler, and workers must all run on the same node in the Kubernetes cluster.
* Airbyte passes records inefficiently between pods by `kubectl attach`-ing to pods using `kubectl run`.
* The provided manifests do not easily allow configuring a non-default namespace.
* Latency for UI operations is high.
* We don't clean up completed worker job and pod histories. 
  * All records replicated are also logged to the Kubernetes logging service. 
  * Logs, events, and job/pod histories require manual deletion.
* Please let us know on [Slack](https://slack.airbyte.io):
  * if those issues are blocking your adoption of Airbyte.
  * if you encounter any other issues or limitations of our Kube implementation.
  * if you'd like to make contributions to fix some of these issues!

## Creating Testing Clusters

* Local \(Mac\)
  * Install [Docker for Mac](https://docs.docker.com/docker-for-mac/install/)
  * Under `Preferences` enable Kubernetes.
  * Use `kubectl config get-contexts` to show the contexts available.
  * Use the Docker UI or `kubectl use-context <docker desktop context>` to access the cluster with `kubectl`.
* Local \(Linux\)
  * Consider using a tool like [Minikube](https://minikube.sigs.k8s.io/docs/start/) to start a local cluster.
* GKE
  * Configure `gcloud` with `gcloud auth login`.
  * [Create a cluster with the command line or the Cloud Console UI](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster)
  * If you created the cluster on the command line, the context will be written automatically.
  * If you used the UI, you can copy and paste the command used to connect from the cluster page.
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <gke context>` to access the cluster with `kubectl`.
* EKS
  * [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
  * Install [eksctl](https://eksctl.io/introduction/)
  * Run `eksctl create cluster` to create an EKS cluster/VPC/subnets/etc.
    * This should take 10-15 minutes.
    * The default settings should be able to support running Airbyte.
  * Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to `kubectl`
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <eks context>` to access the cluster with `kubectl`.

## Kustomize

We use [Kustomize](https://kustomize.io/), which is built into `kubectl` to allow overrides for different environments.

Our shared resources are in the `kube/resources` directory, and we define overlays for each environment. We recommend creating your own overlay if you want to customize your deployments.

Example `kustomization.yaml` file:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - https://github.com/airbytehq/airbyte.git/kube/overlays/stable?ref=master
```

This would allow you to define custom resources or extend existing resources, even within your own VCS.

## View Raw Manifests

For a specific overlay, you can run `kubectl kustomize kube/overlays/stable` to view the manifests that Kustomize will apply to your Kubernetes cluster. This is useful for debugging because it will show the exact resources you are defining.

## Resizing Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported for your type of mount. For a production instance, it's useful to track the usage of volumes to ensure they don't run out of space.

## Copy Files To/From Volumes

See the documentation for [`kubectl cp`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp).

## Dev Iteration \(on local Kubernetes clusters\)

If you're developing using a local context and are not using your local Kubernetes instance for anything else, you can iterate with the following series of commands.

```bash
./gradlew composeBuild # build dev images
kubectl delete -k kube/overlays/dev # optional, if you want to try recreating resources
kubectl apply -k kube/overlays/dev # applies manifests
```

Then restart the port-forwarding commands.

Note: this does not remove jobs and pods created for Airbyte workers.

If you are in a dev environment on a local cluster only running Airbyte and want to start completely from scratch, you can use the following command to destroy everything on the cluster:

```bash
# BE CAREFUL, THIS COMMAND DELETES ALL RESOURCES, EVEN NON-AIRBYTE ONES!
kubectl delete "$(kubectl api-resources --namespaced=true --verbs=delete -o name | tr "\n" "," | sed -e 's/,$//')" --all
```

## Dev Iteration \(on GKE\)

The process is similar to developing on a local cluster, except you will need to build the local version and push it to your own container registry with names such as `your-registry/scheduler`. Then you will need to configure an overlay to override the name of images and apply your overlay with `kubectl apply -k <path to your overlay`.

## Listing Files

```bash
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx ls /tmp/workspace/8
```

## Reading Files

```bash
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx cat /tmp/workspace/8/0/logs.log
```


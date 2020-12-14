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
1. `kubectl port-forward svc/airbyte-webapp-svc 8000:80`
1. `kubectl port-forward svc/airbyte-server-svc 8001:8001`
1. Go to http://localhost:8000/

Coding todos:
todo: better version handling
todo: manually test end to end sync
todo: repeatable testing for kube using k3s in CI
todo: merge master
todo: add segment tracking of identity type

Documentation todos:
todo: document how to resize airbyte-volume-local and how to put files onto it for local file testing with `kubectl cp`
todo: how to bump local or workspace volume size if running out of space
todo: how to read data from workspace or local volumes
todo: how to connect to the db and read from it
todo: show how to iterate with `./gradlew composeBuild && (kubectl delete --grace-period=0 --force -k kube/overlays/dev || true) && kubectl apply -k kube/overlays/dev` or with a way that doesn't clobber configs
todo: show how to delete everything: `kubectl delete "$(kubectl api-resources --namespaced=true --verbs=delete -o name | tr "\n" "," | sed -e 's/,$//')" --all`

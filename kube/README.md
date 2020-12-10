How to Run Airbyte from Kube

1. Apply 
1. Wait for pods to be "Running" on `kubectl get pods | grep airbyte`
1. `kubectl port-forward svc/airbyte-webapp-svc 8000:80`
1. `kubectl port-forward svc/airbyte-server-svc 8001:8001`
1. Go to http://localhost:8000/

todo: document how to resize airbyte-volume-local and how to put files onto it for local file testing
todo: how to bump local or workspace volume size if running out of space
todo: how to read data from workspace or local volumes
todo: how to connect to the db and read from it
todo: move db secrets to kube secrets?
todo: either make a port forwarding thing that works for pod restarts or document the timing out behavior
todo: working local kube with job launching
todo: testing for kube
todo: kube on gke
todo: easy way of running dev versions/change other env variables
todo: use non-mounted space for buffers so it’s faster?

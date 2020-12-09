How to Run Airbyte from Kube

1. Apply 
1. `kubectl port-forward svc/airbyte-webapp-svc 8000:80`
1. Go to http://localhost:8000/

todo: document how to resize airbyte-volume-local and how to put files onto it for local file testing
todo: how to bump local or workspace volume size if running out of space
todo: how to read data from workspace or local volumes

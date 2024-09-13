# Scaling Airbyte

Airbyte is broken into two high level components, the control plane and the data plane. The control plane can be thought
of as the UI, and the services that are needed to power the UI. The control plane is a relatively stable load on your 
system, while the data plane will fluctuate resource usage depending on the jobs that Airbyte is running. Both the 
control plane and data plane can be scaled through creating a values.yaml file and deploying your Airbyte instance.

## Scaling the control plane

Each service can be scaled independently.

### Jobs

```yaml
  # Jobs resource requests and limits, see http://kubernetes.io/docs/user-guide/compute-resources/
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube.
global:
  jobs:
    resources:
      ## Example:
      ## requests:
      ##    memory: 256Mi
      ##    cpu: 250m
      # -- Job resource requests
      requests: {}
      ## Example:
      ## limits:
      ##    cpu: 200m
      ##    memory: 1Gi
      # -- Job resource limits
      limits: {}
```

### Webapp

```yaml
  ## Web app resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
global:
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the Web container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the Web container
    requests: {}
```

### Airbyte Server

```yaml
  ## server resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
global:
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the server container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the server container
    requests: {}
```

## Scaling the data plane

Worker v2
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Values.yaml reference

This is the complete reference for Airbyte's values.yaml file. Use the one that corresponds to the version of the Helm chart you're implementing. 
<!-- More information: [For Community](chart-v2-community), [For Enterprise](../enterprise-setup/chart-v2-enterprise). -->

<Tabs>
  <TabItem value="helm-1" label="Helm chart V1" default>

```yaml
# Global params that are overwritten with umbrella chart
global:
  # -- Service Account name override
  serviceAccountName: &service-account-name "airbyte-admin"
  # -- Edition; "community" or "enterprise"
  edition: "community"

  enterprise:
    # -- Secret name where an Airbyte license key is stored
    secretName: "airbyte-config-secrets"
    # -- The key within `licenseKeySecretName` where the Airbyte license key is stored
    licenseKeySecretKey: "license-key"

  # -- The URL where Airbyte will be reached; This should match your Ingress host
  airbyteUrl: ""

  # Docker image config that will apply to all images.
  image:
    # Docker registry to pull platform images from, e.g. http://my-registry:8000/
    registry: ""
    # Image tag to use for airbyte images. 
    # Does not include non-airbyte images such as temporal, minio, etc.
    tag: ""

  # Docker image pull secret
  imagePullSecrets: []

  # -- Auth configuration
  auth:
    # -- Whether auth is enabled
    enabled: false
    # -- Admin user configuration
    instanceAdmin:
      # -- Secret name where the instanceAdmin configuration is stored
      secretName: "airbyte-config-secrets"
      # -- The first name of the initial user
      firstName: ""
      # -- The last name of the initial user
      lastName:  ""
      # -- The key within `emailSecretName` where the initial user's email is stored
      emailSecretKey: "instance-admin-email"
      # -- The key within `passwordSecretName` where the initial user's password is stored
      passwordSecretKey: "instance-admin-password"
    
    # -- SSO Identify Provider configuration; (requires Enterprise)
    #identityProvider:
    #  # -- Secret name where the OIDC configuration is stored
    #  secretName: "airbyte-config-secrets"
    #  # -- The identity provider type (e.g. oidc)
    #  type: ""
    #  # -- OIDC configuration (required if `auth.identityProvider.type` is "oidc")
    #  oidc:
    #    # -- OIDC application domain
    #    domain: ""
    #    # -- OIDC application name
    #    appName: ""
    #    # -- OIDC application display name (sets the name to present to the user on the login form, defaults to appName if not set)  
    #    displayName: ""
    #    # -- The key within `clientIdSecretName` where the OIDC client id is stored
    #    clientIdSecretKey: "client-id"
    #    # -- The key within `clientSecretSecretName` where the OIDC client secret is stored
    #    clientSecretSecretKey: "client-secret"

  # -- Environment variables
  env_vars: {}

  # -- Database configuration
  database:
    type: "internal" # "external"

    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"

    # -- The database host
    host: ""

    # -- The database port
    port: ""

    # -- The database name
    database: ""

    # -- The database user
    user: ""
    # -- The key within `secretName` where the user is stored
    #userSecretKey: "" # e.g. "database-user"

    # -- The database password
    password: ""
    # -- The key within `secretName` where the password is stored
    #passwordSecretKey: "" # e.g."database-password"



  storage:
    # -- The storage backend type. Supports s3, gcs, azure, minio (default)
    type: minio # default storage used
    # -- Secret name where storage provider credentials are stored
    #storageSecretName: "airbyte-config-secrets"

    # S3
    #bucket: ## S3 bucket names that you've created. We recommend storing the following all in one bucket.
    #  log: airbyte-bucket
    #  state: airbyte-bucket
    #  workloadOutput: airbyte-bucket
    #s3:
    #  region: "" ## e.g. us-east-1
    #  authenticationType: credentials ## Use "credentials" or "instanceProfile"

    # GCS
    #bucket: ## GCS bucket names that you've created. We recommend storing the following all in one bucket.
    #  log: airbyte-bucket
    #  state: airbyte-bucket
    #  workloadOutput: airbyte-bucket
    #gcs:
    #  projectId: <project-id>
    #  credentialsJson: /secrets/gcs-log-creds/gcp.json

    # Azure
    #bucket: ## Azure Blob Storage container names that you've created. We recommend storing the following all in one bucket.
    #  log: airbyte-bucket
    #  state: airbyte-bucket
    #  workloadOutput: airbyte-bucket
    #azure:
    #  # one of the following: connectionString, connectionStringSecretKey
    #  connectionString: <azure storage connection string>
    #  connectionStringSecretKey: <secret coordinate containing an existing connection-string secret>

  metrics:
    enabled: "false"
    step: ""
    otlp:
      enabled: "false"
      # -- The open-telemetry-collector endpoint that metrics will be sent to
      collectorEndpoint: ""
    statsd:
      enabled: "false"
      flavor: ""
      host: ""
      port: ""

  # Jobs resource requests and limits, see http://kubernetes.io/docs/user-guide/compute-resources/
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube.
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

    local:
      volume:
        enabled: false

    kube:
      ## JOB_KUBE_ANNOTATIONS
      # pod annotations of the sync job and the default pod annotations fallback for others jobs
      # -- key/value annotations applied to kube jobs
      annotations: {}

      ## JOB_KUBE_LABELS
      ## pod labels of the sync job and the default pod labels fallback for others jobs
      # -- key/value labels applied to kube jobs
      labels: {}

      ## JOB_KUBE_NODE_SELECTORS
      ## pod node selector of the sync job and the default pod node selector fallback for others jobs
      # -- Node labels for pod assignment
      nodeSelector: {}

      ## JOB_KUBE_TOLERATIONS
      # -- Node tolerations for pod assignment
      #  Any boolean values should be quoted to ensure the value is passed through as a string.
      tolerations: []

      ## JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET
      # -- image pull secret to use for job pod
      main_container_image_pull_secret: ""

## @section Common Parameters

# -- String to partially override airbyte.fullname template with a string (will prepend the release name)
nameOverride: ""
# -- String to fully override airbyte.fullname template with a string
fullnameOverride: ""

# Pods Service Account, see https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
serviceAccount:
  # -- Specifies whether a ServiceAccount should be created
  create: true
  # -- Annotations for service account. Evaluated as a template. Only used if `create` is `true`.
  annotations: {}
  # -- Name of the service account to use. If not set and create is true, a name is generated using the fullname template.
  name: *service-account-name

# -- Sets the AIRBYTE_VERSION environment variable. Defaults to Chart.AppVersion.
## If changing the image tags below, you should probably also update this.
version: ""

## @section Ingress Parameters

# -- Top-level ingress configuration for the entire Airbyte deployment.
# This allows you to create a single ingress resource that routes to multiple services
# based on paths, independent of individual component ingress settings.
ingress:
  # -- Set to true to enable top-level ingress record generation
  enabled: false
  # -- Specifies ingressClassName for clusters >= 1.18+
  className: ""

  annotations: {}
    # nginx.ingress.kubernetes.io/ssl-redirect: "false"
  # -- Custom ingress TLS configuration
  tls: []
    # - hosts:
    #   - airbyte.example.com
    #   secretName: airbyte-tls
  # -- Ingress rules configuration
  rules:
    # -- Hostname for the ingress rule
    - host: ""
      # -- List of paths for this host
      paths:
        # note: the /auth path should only be set if you are using keycloak for auth
        # - path: /auth
        #   pathType: Prefix
        #   service:
        #     name: "{{ .Release.Name }}-airbyte-keycloak-svc"
        #     port: 8180
        # - path: /api/v1/connector_builder/
        #   pathType: Prefix
        #   service:
        #     name: "{{ .Release.Name }}-connector-builder-server-svc"
        #     port: 80
        # - path: /
        #   pathType: Prefix
        #   service:
        #     name: "{{ .Release.Name }}-airbyte-server-svc"
        #     port: 8001


## @section Webapp Parameters

webapp:
  enabled: true
  # -- Number of webapp replicas
  replicaCount: 1

  ##  webapp.image.repository
  ##  webapp.image.pullPolicy
  ##  webapp.image.tag The airbyte webapp image tag. Defaults to the chart's AppVersion
  image:
    # -- The repository to use for the airbyte webapp image
    repository: airbyte/webapp
    # -- The pull policy to use for the airbyte webapp image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the webapp pods
  podAnnotations: {}

  # -- webapp.podLabels [object] Add extra labels to the webapp pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## Configure extra options for the webapp containers' liveness and readiness probes,
  ## see https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#configure-probes
  livenessProbe:
    # -- Enable livenessProbe on the webapp
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 1
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the webapp
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 1
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  service:
    # -- The service type to use for the webapp service
    type: ClusterIP
    # -- The service port to expose the webapp on
    port: 80
    # -- Annotations for the webapp service resource
    annotations: {}

  ## Web app resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
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

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  ## Configure the ingress resource that allows you to access the Airbyte installation.
  ## ref: http://kubernetes.io/docs/user-guide/ingress/
  ingress:
    # -- Set to true to enable ingress record generation
    enabled: false
    # -- Specifies ingressClassName for clusters >= 1.18+
    className: ""
    # -- Ingress annotations done as key:value pairs
    annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
    # -- The list of hostnames to be covered with this ingress record.
    hosts: []
    # - host: chart-example.local
    #   paths:
    #   - path: /
    #     pathType: ImplementationSpecific
    # -- Custom ingress TLS configuration
    tls: []
    # - secretName: chart-example-tls
    #   hosts:
    #   - chart-example.local

  api:
    # -- The webapp API url
    url: /api/v1/

  fullstory:
    # -- Whether to enable fullstory
    enabled: false

  ## Examples (when using `webapp.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: var-run
  ##     mountPath: /var/run/
  ##   - name: var-cache-nginx
  ##     mountPath: /var/cache/nginx
  ##   - mountPath: /etc/nginx/conf.d
  ##     name: nginx-conf-d
  ##
  # -- Additional volumeMounts for webapp containers
  extraVolumeMounts: []

  ## Examples (when using `webapp.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: var-run
  ##     emptyDir: {}
  ##   - name: var-cache-nginx
  ##     emptyDir: {}
  ##   - name: nginx-conf-d
  ##     emptyDir: {}
  # -- Additional volumes for webapp pods
  extraVolumes: []

  ## Example:
  # extraContainers:
  #   - name: otel_collector
  #     image: somerepo/someimage:sometag
  #     args: [
  #         "--important-args"
  #     ]
  #     ports:
  #       - containerPort: 443
  #     volumeMounts:
  #       - name: volumeMountCool
  #         mountPath: /some/path
  #         readOnly: true
  # -- Additional container for server pods
  extraContainers: []

  ## Example:
  # extraInitContainers:
  #   - name: sleepy
  #     image: alpine
  #     command: ['sleep', '60']
  # -- Additional init containers for server pods
  extraInitContainers: []

  ## Example: (With default env vars and values taken from generated config map)
  # extraEnv:
  #   - name: POSTGRES_USER
  #     valueFrom:
  #       secretKeyRef:
  #         name: airbyte-secrets
  #         key: DATABASE_USER
  #   - name: POSTGRES_PWD
  #     valueFrom:
  #       secretKeyRef:
  #         name: airbyte-secrets
  #         key: DATABASE_PASSWORD
  #   - name: DYNAMIC_CONFIG_FILE_PATH
  #     value: "config/dynamicconfig/development.yaml"
  #   - name: DB
  #     value: "postgresql"
  #   - name: DB_PORT
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: DATABASE_PORT
  #   - name: POSTGRES_SEEDS
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: DATABASE_HOST
  # -- Supply extra env variables to main container using full notation
  extraEnv: []
  ## Example:
  ## secrets:
  ##   DATABASE_PASSWORD: strong-password
  ##   DATABASE_USER: my-db-user
  # -- Supply additional secrets to container
  secrets: {}

  ## Example:
  ## env_vars:
  ##   DATABASE_HOST: airbyte-db
  ##   DATABASE_PORT: 5432
  # -- Supply extra env variables to main container using simplified notation
  env_vars: {}

## @section Server parameters

server:
  enabled: true
  # -- Number of server replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte server image.
    repository: airbyte/server
    # -- the pull policy to use for the airbyte server image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the server pods
  podAnnotations: {}

  # -- Add extra labels to the server pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## Configure extra options for the server containers' liveness and readiness probes
  ## ref: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#configure-probes
  livenessProbe:
    # -- Enable livenessProbe on the server
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 10
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the server
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 10
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## server resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
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

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for server pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for server pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  log:
    # -- The log level to log at
    level: "INFO"

  ## Examples (when using `server.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for server containers
  extraVolumeMounts: []

  ## Examples (when using `server.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for server pods
  extraVolumes: []

  ## Example:
  # extraContainers:
  #   - name: otel_collector
  #     image: somerepo/someimage:sometag
  #     args: [
  #         "--important-args"
  #     ]
  #     ports:
  #       - containerPort: 443
  #     volumeMounts:
  #       - name: volumeMountCool
  #         mountPath: /some/path
  #         readOnly: true
  # -- Additional container for server pods
  extraContainers: []

  ## Example:
  # extraInitContainers:
  #   - name: sleepy
  #     image: alpine
  #     command: ['sleep', '60']
  # -- Additional init containers for server pods
  extraInitContainers: []

  ## Example: (With default env vars and values taken from generated config map)
  # extraEnv:
  #   - name: AIRBYTE_VERSION
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: AIRBYTE_VERSION
  #   - name: API_URL
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: API_URL
  #   - name: TRACKING_STRATEGY
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: TRACKING_STRATEGY
  #   - name: FULLSTORY
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: FULLSTORY
  #   - name: INTERNAL_API_HOST
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: INTERNAL_API_HOST
  ##
  # -- Supply extra env variables to main container using full notation
  extraEnv: []
  ## Example:
  ## secrets:
  ##   DATABASE_PASSWORD: strong-password
  ##   DATABASE_USER: my-db-user
  # -- Supply additional secrets to container
  secrets: {}
  ## Example:
  ## env_vars:
  ##   DATABASE_HOST: airbyte-db
  ##   DATABASE_PORT: 5432
  # -- Supply extra env variables to main container using simplified notation
  env_vars: {}

## @section Worker Parameters

worker:
  enabled: true
  # -- Number of worker replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte worker image.
    repository: airbyte/worker
    # -- the pull policy to use for the airbyte worker image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the worker pods
  podAnnotations: {}

  # -- Add extra labels to the worker pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the worker
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 1
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the worker
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 1
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## worker resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    #! -- The resources limits for the worker container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the worker container
    requests: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for worker pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for worker pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  log:
    #! -- The log level to log at.
    level: "INFO"

  ## Example:
  ##
  ## extraEnv:
  ## - name: JOB_KUBE_TOLERATIONS
  ##   value: "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule"
  # -- Additional env vars for worker pods
  extraEnv: []

  ## Examples (when using `worker.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for worker containers
  extraVolumeMounts: []

  ## Examples (when using `worker.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for worker pods
  extraVolumes: []
  # -- Additional container for worker pods
  extraContainers: []

  hpa:
    enabled: false

  debug:
    enabled: false

  ## current no exist documentations
  activityMaxAttempt: ""
  activityInitialDelayBetweenAttemptsSeconds: ""
  activityMaxDelayBetweenAttemptsSeconds: ""
  maxNotifyWorkers: 5

## @section Workload Launcher Parameters

workload-launcher:
  enabled: true
  # -- Number of workload launcher replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte workload launcher image.
    repository: airbyte/workload-launcher
    # -- The pull policy to use for the airbyte workload launcher image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the workload launcher pods
  podAnnotations: {}

  # -- Add extra labels to the workload launcher pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the workload launcher
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 1
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the workload launcher
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 1
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## workload launcher resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the workload launcher container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the workload launcher container
    requests: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for workload launcher pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # Affinity and anti-affinity for workload launcher pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  log:
    # -- The log level to log at
    level: "INFO"

  ## Example:
  ##
  ## extraEnv:
  ## - name: JOB_KUBE_TOLERATIONS
  ##   value: "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule"
  # -- Additional env vars for workload launcher pods
  extraEnv: []

  ## Examples (when using `workload launcher.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for workload launcher containers
  extraVolumeMounts: []

  ## Examples (when using `workload-launcher.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for workload launcher pods
  extraVolumes: []

  extraContainers: []

  hpa:
    enabled: false

  debug:
    enabled: false

  containerOrchestrator:
    # -- Enable or disable Orchestrator
    enabled: true
    # -- Orchestrator image
    # This is a template string that will be passed to the "tpl" helper.
    image: "airbyte/container-orchestrator:{{ default .Chart.AppVersion .Values.global.image.tag }}"

  connectorSidecar:
    # -- Connector Sidecar image
    # This is a template string that will be passed to the "tpl" helper.
    image: "airbyte/connector-sidecar:{{ default .Chart.AppVersion .Values.global.image.tag }}"

  workloadInit:
    # -- Workload init image
    # This is a template string that will be passed to the "tpl" helper.
    image: "airbyte/workload-init-container:{{ default .Chart.AppVersion .Values.global.image.tag }}"

  connectorProfiler:
    # -- Workload init image
    # This is a template string that will be passed to the "tpl" helper.
    image: "airbyte/async-profiler:{{ default .Chart.AppVersion .Values.global.image.tag }}"

  ## current no exist documentations
  activityMaxAttempt: ""
  activityInitialDelayBetweenAttemptsSeconds: ""
  activityMaxDelayBetweenAttemptsSeconds: ""

  maxNotifyWorkers: 5

## @section Rollout Worker Parameters

connector-rollout-worker:
  enabled: false
  # -- Number of connector rollout worker replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte connector rollout worker image.
    repository: airbyte/connector-rollout-worker
    # -- The pull policy to use for the airbyte connector rollout worker image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the connector rollout worker pods
  podAnnotations: {}

  # -- Add extra labels to the connector rollout worker pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the connector rollout worker
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 1
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the connector rollout worker
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 1
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## connector rollout worker resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the connector rollout worker container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the connector rollout worker container
    requests: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for connector rollout worker pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # Affinity and anti-affinity for connector rollout worker pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  log:
    # -- The log level to log at
    level: "INFO"

  ## Example:
  ##
  ## extraEnv:
  ## - name: JOB_KUBE_TOLERATIONS
  ##   value: "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule"
  # -- Additional env vars for connector rollout worker pods
  extraEnv: []

  ## Examples (when using `connector rollout worker.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for connector rollout worker containers
  extraVolumeMounts: []

  ## Examples (when using `connector-rollout-worker.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for connector rollout worker pods
  extraVolumes: []

  extraContainers: []

  hpa:
    enabled: false

  debug:
    enabled: false

  containerOrchestrator:
    # -- Enable or disable Orchestrator
    enabled: true
    # -- Orchestrator image
    image: ""

  ## current no exist documentations
  activityMaxAttempt: ""
  activityInitialDelayBetweenAttemptsSeconds: ""
  activityMaxDelayBetweenAttemptsSeconds: ""

  maxNotifyWorkers: 5

## @section Metrics parameters
metrics:
  enabled: false

  # -- Number of metrics-reporter replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte metrics-reporter image.
    repository: airbyte/metrics-reporter
    # -- The pull policy to use for the airbyte metrics-reporter image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the metrics-reporter pod
  podAnnotations: {}

  # -- Add extra labels to the metrics-reporter pod
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## metrics-reporter app resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the metrics-reporter container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the metrics-reporter container
    requests: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for metrics-reporter pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for metrics-reporter pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  ## Example:
  ##
  ## extraEnv:
  ## - name: SAMPLE_ENV_VAR
  ##   value: "key=sample-value"
  # -- Additional env vars for metrics-reporter pods
  extraEnv: []

  ## Examples (when using `metrics.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for metrics-reporter containers
  extraVolumeMounts: []

  ## Examples (when using `metrics.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for metrics-reporter pods
  extraVolumes: []

  extraContainers: []

  secrets: {}

  env_vars: {}

## @section Bootloader Parameters

airbyte-bootloader:
  enabled: true
  image:
    # -- The repository to use for the airbyte bootloader image.
    repository: airbyte/bootloader
    # -- The pull policy to use for the airbyte bootloader image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the bootloader pod
  podAnnotations: {}

  # -- Add extra labels to the bootloader pod
  podLabels: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for worker pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  ## Bootloader resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the airbyte bootloader image
    requests: {}
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the airbyte bootloader image
    limits: {}

  # -- Affinity and anti-affinity for bootloader pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## Example: (With default env vars and values taken from generated config map)
  ## extraEnv:
  ##   - name: AIRBYTE_VERSION
  ##     valueFrom:
  ##       configMapKeyRef:
  ##         name: airbyte-env
  ##         key: AIRBYTE_VERSION
  ##   - name: DATABASE_HOST
  ##     valueFrom:
  ##       configMapKeyRef:
  ##         name: airbyte-env
  ##         key: DATABASE_HOST
  ##   - name: DATABASE_PORT
  ##     valueFrom:
  ##       configMapKeyRef:
  ##         name: airbyte-env
  ##         key: DATABASE_PORT
  ##   - name: DATABASE_PASSWORD
  ##     valueFrom:
  ##       secretKeyRef:
  ##         name: airbyte-secrets
  ##         key: DATABASE_PASSWORD
  ##   - name: DATABASE_URL
  ##     valueFrom:
  ##       configMapKeyRef:
  ##         name: airbyte-env
  ##         key: DATABASE_URL
  ##   - name: DATABASE_USER
  ##     valueFrom:
  ##       secretKeyRef:
  ##         name: airbyte-secrets
  ##         key: DATABASE_USER
  # -- Supply extra env variables to main container using full notation
  extraEnv: []
  ## Example:
  ## secrets:
  ##   DATABASE_PASSWORD: strong-password
  ##   DATABASE_USER: my-db-user
  # -- Supply additional secrets to container
  secrets: {}

  ## Example:
  ## env_vars:
  ##   DATABASE_HOST: airbyte-db
  ##   DATABASE_PORT: 5432
  # -- Supply extra env variables to main container using simplified notation
  env_vars: {}
  ## Example:
  # extraContainers:
  #   - name: otel_collector
  #     image: somerepo/someimage:sometag
  #     args: [
  #         "--important-args"
  #     ]
  #     ports:
  #       - containerPort: 443
  #     volumeMounts:
  #       - name: volumeMountCool
  #         mountPath: /some/path
  #         readOnly: true
  # -- Additional container for server pod(s)
  extraContainers: []

  ## Example:
  # extraInitContainers:
  #   - name: sleepy
  #     image: alpine
  #     command: ['sleep', '60']
  # -- Additional init containers for server pods
  extraInitContainers: []

  ## Examples (when using `containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for server containers
  extraVolumeMounts: []

  ## Examples (when using `containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for server pods
  extraVolumes: []

## @section Temporal parameters
## TODO: Move to consuming temporal from a dedicated helm chart

temporal:
  enabled: true
  # -- The number of temporal replicas to deploy
  replicaCount: 1

  image:
    # -- The temporal image repository to use
    repository: temporalio/auto-setup
    # -- The pull policy for the temporal image
    pullPolicy: IfNotPresent
    # -- The temporal image tag to use
    tag: "1.27.2"

  service:
    # -- The Kubernetes Service Type
    type: ClusterIP
    # -- The temporal port and exposed kubernetes port
    port: 7233

  # -- Add extra annotations to the temporal pod
  podAnnotations: {}

  # -- Add extra labels to the temporal pod
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(temporal)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(temporal)
    runAsUser: 1000
    # gid=1000(temporal)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraInitContainers:
  ##   - name: config-loader
  ##     image: temporalio/auto-setup:1.27.2
  ##     command:
  ##       - /bin/sh
  ##       - -c
  ##       - >-
  ##         find /etc/temporal/config/ -maxdepth 1 -mindepth 1 -exec cp -ar {} /config/ \;
  ##     volumeMounts:
  ##       - name: config
  ##         mountPath: /config
  # -- Additional InitContainers to initialize the pod
  extraInitContainers: []

  livenessProbe:
    # -- Enable livenessProbe on the temporal
    enabled: false

  readinessProbe:
    # -- Enable readinessProbe on the temporal
    enabled: false

  # -- Node labels for temporal pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for temporal pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for temporal pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  ## Example:
  ##
  ## extraEnv:
  ## - name: SAMPLE_ENV_VAR
  ##   value: "key=sample-value"
  # -- Additional env vars for temporal pod(s).
  extraEnv: []

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  ##   - name: config
  ##     mountPath: /etc/temporal/config
  # -- Additional volumeMounts for temporal containers
  extraVolumeMounts: []

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  ##  - name: config
  ##    emptyDir: {}
  # -- Additional volumes for temporal pods
  extraVolumes: []

  ## Temporal resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for temporal pods
    requests: {}
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for temporal pods
    limits: {}

  extraContainers: []

## @section Temporal parameters
## TODO: Move to consuming temporal from a dedicated helm chart

temporal-ui:
  enabled: false
  # -- The number of temporal-ui replicas to deploy
  replicaCount: 1

  image:
    # -- The temporal-ui image repository to use
    repository: temporalio/ui
    # -- The pull policy for the temporal-ui image
    pullPolicy: IfNotPresent
    tag: "2.30.1"

  service:
    # -- The Kubernetes Service Type
    type: ClusterIP
    # -- The temporal-ui port and exposed kubernetes port
    port: 8088

  # -- Add extra annotations to the temporal-ui pod
  podAnnotations: {}

  # -- Add extra labels to the temporal-ui pod
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(temporal-ui)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false
    runAsNonRoot: false
    # uid=1000(temporal-ui)
    runAsUser: 0
    # gid=1000(temporal-ui)
    runAsGroup: 0
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraInitContainers:
  ##   - name: config-loader
  ##     image: temporalio/ui:2.30.1
  ##     command:
  ##       - /bin/sh
  ##       - -c
  ##       - >-
  ##         find /etc/temporal/config/ -maxdepth 1 -mindepth 1 -exec cp -ar {} /config/ \;
  ##     volumeMounts:
  ##       - name: config
  ##         mountPath: /config
  # -- Additional InitContainers to initialize the pod
  extraInitContainers: []

  livenessProbe:
    # -- Enable livenessProbe on the temporal-ui
    enabled: false

  readinessProbe:
    # -- Enable readinessProbe on the temporal-ui
    enabled: false

  # -- Node labels for temporal-ui pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for temporal-ui pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for temporal-ui pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  ## Example:
  ##
  ## extraEnv:
  ## - name: SAMPLE_ENV_VAR
  ##   value: "key=sample-value"
  # -- Additional env vars for temporal-ui pod(s).
  extraEnv: []

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  ##   - name: config
  ##     mountPath: /etc/temporal/config
  # -- Additional volumeMounts for temporal containers
  extraVolumeMounts: []

  ## Examples (when using `temporal.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  ##  - name: config
  ##    emptyDir: {}
  # -- Additional volumes for temporal-ui pods
  extraVolumes: []

  ## Temporal UI resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for temporal-ui pods
    requests: {}
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for temporal-ui pods
    limits: {}

  extraContainers: []

## @section Airbyte Database parameters

# PostgreSQL chart configuration, see https://github.com/bitnami/charts/blob/master/bitnami/postgresql/values.yaml
postgresql:
  # -- Switch to enable or disable the PostgreSQL helm chart
  enabled: true

  ## image.repository Repository for airbyte-db statefulset
  image:
    repository: airbyte/db
  # -- Airbyte Postgresql username
  postgresqlUsername: airbyte
  # -- Airbyte Postgresql password
  postgresqlPassword: airbyte
  # -- Airbyte Postgresql database
  postgresqlDatabase: db-airbyte
  # fullnameOverride: *db-hostname
  ## This secret is used in case of postgresql.enabled=true and we would like to specify password for newly created postgresql instance
  # -- Name of an existing secret containing the PostgreSQL password ('postgresql-password' key)
  existingSecret: ""
  podSecurityContext:
    # gid=70(postgres)
    fsGroup: 70
  containerSecurityContext:
    # -- Ensures the container will run with a non-root user
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=70(postgres)
    runAsUser: 70
    # gid=70(postgres)
    runAsGroup: 70
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  commonAnnotations:
    # -- It will determine when the hook should be rendered
    helm.sh/hook: pre-install
    # -- The order in which the hooks are executed. If weight is lower, it has higher priority
    helm.sh/hook-weight: "-1"
  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for postgresql pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for postgresql pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

minio:
  image:
    # -- Minio image used by Minio helm chart
    repository: minio/minio
    # -- Minio tag image
    tag: RELEASE.2023-11-20T22-40-07Z

  storage:
    volumeClaimValue: 500Mi

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  ##
  nodeSelector: {}

  # -- Tolerations for minio pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  ##
  tolerations: []

  # -- Affinity and anti-affinity for minio pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  resources:
     requests:
       memory: 1Gi
       cpu: 250m
     limits:
       cpu: 300m
       memory: 2Gi
## @section cron parameters
cron:
  enabled: true
  # -- Number of cron replicas
  replicaCount: 1
  image:
    # -- The repository to use for the airbyte cron image.
    repository: airbyte/cron
    # -- The pull policy to use for the airbyte cron image
    pullPolicy: IfNotPresent

  # -- Add extra annotations to the cron pods
  podAnnotations: {}

  # -- Add extra labels to the cron pods
  podLabels: {}

  # -- Security context for the container
  podSecurityContext:
    # uid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the cron
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 1
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the cron
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 1
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## cron resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the cron container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the cron container
    requests: {}

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for cron pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for cron pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  log:
    # -- The log level to log at.
    level: "INFO"

  ## Examples (when using `cron.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumeMounts:
  ##   - name: tmpdir
  ##     mountPath: /tmp
  # -- Additional volumeMounts for cron containers
  extraVolumeMounts: []

  ## Examples (when using `cron.containerSecurityContext.readOnlyRootFilesystem=true`):
  ## extraVolumes:
  ##   - name: tmpdir
  ##     emptyDir: {}
  # -- Additional volumes for cron pods
  extraVolumes: []

  ## Example:
  # extraContainers:
  #   - name: otel_collector
  #     image: somerepo/someimage:sometag
  #     args: [
  #         "--important-args"
  #     ]
  #     ports:
  #       - containerPort: 443
  #     volumeMounts:
  #       - name: volumeMountCool
  #         mountPath: /some/path
  #         readOnly: true
  # -- Additional container for cron pods
  extraContainers: []

  ## Example:
  # extraInitContainers:
  #   - name: sleepy
  #     image: alpine
  #     command: ['sleep', '60']
  # -- Additional init containers for cron pods
  extraInitContainers: []

  ## Example: (With default env vars and values taken from generated config map)
  # extraEnv:
  #   - name: AIRBYTE_VERSION
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: AIRBYTE_VERSION
  #   - name: API_URL
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: API_URL
  #   - name: TRACKING_STRATEGY
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: TRACKING_STRATEGY
  #   - name: FULLSTORY
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: FULLSTORY
  #   - name: INTERNAL_API_HOST
  #     valueFrom:
  #       configMapKeyRef:
  #         name: airbyte-env
  #         key: INTERNAL_API_HOST
  # -- Supply extra env variables to main container using full notation
  extraEnv: []
  ## Example:
  ## secrets:
  ##   DATABASE_PASSWORD: strong-password
  ##   DATABASE_USER: my-db-user
  # -- Supply additional secrets to container
  secrets: {}
  ## Example:
  ## env_vars:
  ##   DATABASE_HOST: airbyte-db
  ##   DATABASE_PORT: 5432
  # -- Supply extra env variables to main container using simplified notation
  env_vars: {}

connector-builder-server:
  enabled: true
  # -- Number of connector-builder-server replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte connector-builder-server image.
    repository: airbyte/connector-builder-server
    # -- The pull policy to use for the airbyte connector-builder-server image
    pullPolicy: IfNotPresent

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the server
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 10
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the server
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 10
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## connector-builder-server resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the connector-builder-server container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the connector-builder-server container
    requests: {}

  log:
    # -- The log level to log at.
    level: "INFO"

  env_vars: {}
  service:
    port: 80

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

keycloak:
  enabled: true
  env_vars: {}

  auth:
    adminUsername: airbyteAdmin
    adminPassword: keycloak123

  image:
    repository: airbyte/keycloak
    pullPolicy: IfNotPresent

  # -- Security context for the container
  podSecurityContext:
    fsGroup: 1000

  initContainers:
    initDb:
      image: "postgres:13-alpine"

  initContainerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault
    
  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

keycloak-setup:
  enabled: true
  env_vars: {}

  image:
    repository: airbyte/keycloak-setup
    pullPolicy: IfNotPresent

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  initContainerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

workload-api-server:
  enabled: true

  bearerToken: token

  # -- workload-api-server replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte-workload-api-server image.
    repository: airbyte/workload-api-server
    # -- The pull policy to use for the airbyte-workload-api-server image
    pullPolicy: IfNotPresent

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false 
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the server
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 10
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the server
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 10
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## airbyte-workload-api-server resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the airbyte-workload-api-server container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the airbyte-workload-api-server container
    requests: {}

  log:
    # -- The log level at which to log
    level: "INFO"

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  env_vars: {}
  service:
    port: 8007

  # Configure the ingress resource that allows you to access the Airbyte Workload API, see http://kubernetes.io/docs/user-guide/ingress/
  ingress:
    # -- Set to true to enable ingress record generation
    enabled: false
    # -- Specifies ingressClassName for clusters >= 1.18+
    className: ""
    # -- Ingress annotations done as key:value pairs
    annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
    # -- The list of hostnames to be covered with this ingress record
    hosts: []
    # - host: chart-example.local
    #   paths:
    #   - path: /
    #     pathType: ImplementationSpecific
    # -- Custom ingress TLS configuration
    tls: []
    # - secretName: chart-example-tls
    #   hosts:
    #   - chart-example.local

featureflag-server:
  enabled: false

  # -- workload-api-server replicas
  replicaCount: 1

  image:
    # -- The repository to use for the airbyte-workload-api-server image.
    repository: airbyte/featureflag-server
    # -- The pull policy to use for the airbyte-workload-api-server image
    pullPolicy: IfNotPresent

  # -- Security context for the container
  podSecurityContext:
    # gid=1000(airbyte)
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false
    runAsNonRoot: true
    # uid=1000(airbyte)
    runAsUser: 1000
    # gid=1000(airbyte)
    runAsGroup: 1000
    readOnlyRootFilesystem: false
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault

  livenessProbe:
    # -- Enable livenessProbe on the server
    enabled: true
    # -- Initial delay seconds for livenessProbe
    initialDelaySeconds: 30
    # -- Period seconds for livenessProbe
    periodSeconds: 10
    # -- Timeout seconds for livenessProbe
    timeoutSeconds: 10
    # -- Failure threshold for livenessProbe
    failureThreshold: 3
    # -- Success threshold for livenessProbe
    successThreshold: 1

  readinessProbe:
    # -- Enable readinessProbe on the server
    enabled: true
    # -- Initial delay seconds for readinessProbe
    initialDelaySeconds: 10
    # -- Period seconds for readinessProbe
    periodSeconds: 10
    # -- Timeout seconds for readinessProbe
    timeoutSeconds: 10
    # -- Failure threshold for readinessProbe
    failureThreshold: 3
    # -- Success threshold for readinessProbe
    successThreshold: 1

  ## airbyte-workload-api-server resource requests and limits
  ## ref: http://kubernetes.io/docs/user-guide/compute-resources/
  ## We usually recommend not to specify default resources and to leave this as a conscious
  ## choice for the user. This also increases chances charts run on environments with little
  ## resources, such as Minikube. If you do want to specify resources, uncomment the following
  ## lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  resources:
    ## Example:
    ## limits:
    ##    cpu: 200m
    ##    memory: 1Gi
    # -- The resources limits for the airbyte-workload-api-server container
    limits: {}
    ## Examples:
    ## requests:
    ##    memory: 256Mi
    ##    cpu: 250m
    # -- The requested resources for the airbyte-workload-api-server container
    requests: {}

  log:
    # -- The log level at which to log
    level: "INFO"

  # -- Node labels for pod assignment, see https://kubernetes.io/docs/user-guide/node-selection/
  nodeSelector: {}

  # -- Tolerations for webapp pod assignment, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []

  # -- Affinity and anti-affinity for webapp pod assignment, see
  # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
  affinity: {}

  env_vars: {}
  service:
    port: 8007

  # Configure the ingress resource that allows you to access the Airbyte Workload API, see http://kubernetes.io/docs/user-guide/ingress/
  ingress:
    # -- Set to true to enable ingress record generation
    enabled: false
    # -- Specifies ingressClassName for clusters >= 1.18+
    className: ""
    # -- Ingress annotations done as key:value pairs
    annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
    # -- The list of hostnames to be covered with this ingress record
    hosts: []
    # - host: chart-example.local
    #   paths:
    #   - path: /
    #     pathType: ImplementationSpecific
    # -- Custom ingress TLS configuration
    tls: []
    # - secretName: chart-example-tls
    #   hosts:
    #   - chart-example.local

testWebapp:
  image:
    repository: airbyte/airbyte-base-java-image
    tag: 3.3.7
```

  </TabItem>
  <TabItem value="helm-2" label="Helm chart V2">

```yaml reference
https://github.com/airbytehq/airbyte-platform/blob/main/charts/v2/airbyte/values.yaml
```

  </TabItem>

</Tabs>

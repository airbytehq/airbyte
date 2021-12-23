{{/*
Expand the name of the chart.
*/}}
{{- define "airbyte.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "airbyte.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "airbyte.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "airbyte.labels" -}}
helm.sh/chart: {{ include "airbyte.chart" . }}
{{ include "airbyte.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "airbyte.selectorLabels" -}}
app.kubernetes.io/name: {{ include "airbyte.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "airbyte.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "airbyte.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "airbyte.postgresql.fullname" -}}
{{- $name := default "postgresql" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Get the Postgresql credentials secret.
*/}}
{{- define "airbyte.postgresql.secretName" -}}
{{- if and (.Values.postgresql.enabled) (not .Values.postgresql.existingSecret) -}}
    {{- printf "%s" (include "airbyte.postgresql.fullname" .) -}}
{{- else if and (.Values.postgresql.enabled) (.Values.postgresql.existingSecret) -}}
    {{- printf "%s" .Values.postgresql.existingSecret -}}
{{- else }}
    {{- if .Values.externalDatabase.existingSecret -}}
        {{- printf "%s" .Values.externalDatabase.existingSecret -}}
    {{- else -}}
        {{ printf "%s-%s" .Release.Name "externaldb" }}
    {{- end -}}
{{- end -}}
{{- end -}}


{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.host" -}}
{{- ternary (include "airbyte.postgresql.fullname" .) .Values.externalDatabase.host .Values.postgresql.enabled -}}
{{- end -}}

{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.user" -}}
{{- ternary .Values.postgresql.postgresqlUsername .Values.externalDatabase.user .Values.postgresql.enabled -}}
{{- end -}}

{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.name" -}}
{{- ternary .Values.postgresql.postgresqlDatabase .Values.externalDatabase.database .Values.postgresql.enabled -}}
{{- end -}}

{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.existingsecret.key" -}}
{{- if .Values.postgresql.enabled -}}
    {{- printf "%s" "postgresql-password" -}}
{{- else -}}
    {{- if .Values.externalDatabase.existingSecret -}}
        {{- if .Values.externalDatabase.existingSecretPasswordKey -}}
            {{- printf "%s" .Values.externalDatabase.existingSecretPasswordKey -}}
        {{- else -}}
            {{- printf "%s" "postgresql-password" -}}
        {{- end -}}
    {{- else -}}
        {{- printf "%s" "postgresql-password" -}}
    {{- end -}}
{{- end -}}
{{- end -}}

{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.port" -}}
{{- ternary "5432" .Values.externalDatabase.port .Values.postgresql.enabled -}}
{{- end -}}

{{/*
Add environment variables to configure database values
*/}}
{{- define "airbyte.database.url" -}}
{{- $host := (include "airbyte.database.host" .) -}}
{{- $dbName := (include "airbyte.database.name" .) -}}
{{- $port := (include "airbyte.database.port" . ) -}}
{{- printf "jdbc:postgresql://%s:%s/%s" $host $port $dbName -}}
{{- end -}}

{{/*
Create a default fully qualified minio name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "airbyte.minio.fullname" -}}
{{- $name := default "minio" .Values.logs.minio.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Add environment variables to configure minio
*/}}
{{- define "airbyte.minio.endpoint" -}}
{{- if .Values.logs.minio.enabled -}}
    {{- printf "http://%s:%d" (include "airbyte.minio.fullname" .) 9000 -}}
{{- else if .Values.logs.externalMinio.enabled -}}
    {{- printf "http://%s:%d" .Values.logs.externalMinio.host .Values.logs.externalMinio.port -}}
{{- else -}}
    {{- printf "" -}}
{{- end -}}
{{- end -}}

{{- define "airbyte.s3PathStyleAccess" -}}
{{- ternary "true" "" (or .Values.logs.minio.enabled .Values.logs.externalMinio.enabled) -}}
{{- end -}}

{{/*
Returns the Airbyte Scheduler Image
*/}}
{{- define "airbyte.schedulerImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.scheduler.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Airbyte Server Image
*/}}
{{- define "airbyte.serverImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.server.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Airbyte Webapp Image
*/}}
{{- define "airbyte.webappImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.webapp.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Airbyte podSweeper Image
*/}}
{{- define "airbyte.podSweeperImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.podSweeper.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Airbyte worker Image
*/}}
{{- define "airbyte.workerImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.worker.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Airbyte Bootloader Image
*/}}
{{- define "airbyte.bootloaderImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.bootloader.image "global" .Values.global) -}}
{{- end -}}

{{/*
Returns the Temporal Image. TODO: This will probably be replaced if we move to using temporal as a dependency, like minio and postgres.
*/}}
{{- define "airbyte.temporalImage" -}}
{{- include "common.images.image" (dict "imageRoot" .Values.temporal.image "global" .Values.global) -}}
{{- end -}}

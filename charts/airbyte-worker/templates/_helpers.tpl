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
Define db secret
*/}}

{{- define "database.secret.name" -}}
{{- printf "%s-postgresql" .Release.Name }}
{{- end }}

{{/* 
Define imageTag
*/}}

{{- define "worker.imageTag" -}}
{{- if .Values.image.tag }}
    {{- printf "%s" .Values.image.tag }}
{{- else if ((.Values.global.image).tag) }}
    {{- printf "%s" .Values.global.image.tag }}
{{- else }}
    {{- printf "%s" .Chart.AppVersion }}
{{- end }}
{{- end }}
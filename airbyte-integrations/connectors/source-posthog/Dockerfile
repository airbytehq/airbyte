FROM airbyte/source-lowcode:dev

# copy payload code only
COPY source_posthog/ source_posthog
COPY source_posthog/spec.* source_lowcode/
COPY source_posthog/posthog.yaml source_lowcode/manifest.yaml

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-posthog
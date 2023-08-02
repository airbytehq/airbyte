FROM google/dart

RUN pub global activate linkcheck

ENTRYPOINT ["/root/.pub-cache/bin/linkcheck"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/tool-link-checker

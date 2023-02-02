##
# Airbyte webapp
#
# This file is an optimization for build commands that generate code. Make only runs a
# target if any of its dependencies has a more recent timestamp than the target file,
# which allows us to unconditionally run those commands every time we would like
# up-to-date generated code (i.e. building, starting a dev server, testing, whatever)
# without having to wait for a blocking call to regenerate identical code.

generate-client: src/core/request/AirbyteClient.ts src/core/request/ConnectorBuilderClient.ts src/core/request/ConnectorManifest.ts

src/core/request/AirbyteClient.ts: ../airbyte-api/src/main/openapi/config.yaml
	echo building AirbyteClient.ts
	npm run generate-client

src/core/request/ConnectorBuilderClient.ts: ../airbyte-connector-builder-server/src/main/openapi/openapi.yaml
	echo building ConnectorBuilderClient.ts
	npm run generate-client

src/core/request/ConnectorManifest.ts: src/services/connectorBuilder/connector_manifest_openapi.yaml
	echo building ConnectorManifest.ts
	npm run generate-client

.PHONY: generate-client

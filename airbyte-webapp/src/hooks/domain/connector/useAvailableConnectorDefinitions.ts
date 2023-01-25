import { useMemo } from "react";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { getExcludedConnectorIds } from "core/domain/connector/constants";
import { WorkspaceRead } from "core/request/AirbyteClient";
import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";

export const useAvailableConnectorDefinitions = <
  T extends SourceDefinitionReadWithLatestTag | DestinationDefinitionReadWithLatestTag | ConnectorDefinition
>(
  connectionDefinitions: T[],
  workspace: WorkspaceRead
): T[] =>
  useMemo(() => {
    const excludedConnectorIds = getExcludedConnectorIds(workspace.workspaceId);
    return connectionDefinitions.filter(
      (connectorDefinition) => !excludedConnectorIds.includes(Connector.id(connectorDefinition))
    );
  }, [connectionDefinitions, workspace.workspaceId]);

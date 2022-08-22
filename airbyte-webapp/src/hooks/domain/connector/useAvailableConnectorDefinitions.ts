import { useMemo } from "react";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { getExcludedConnectorIds } from "core/domain/connector/constants";
import { WorkspaceRead } from "core/request/AirbyteClient";

export const useAvailableConnectorDefinitions = (
  connectionDefinitions: ConnectorDefinition[],
  workspace: WorkspaceRead
) =>
  useMemo(() => {
    const excludedConnectorIds = getExcludedConnectorIds(workspace.workspaceId);
    return connectionDefinitions.filter(
      (connectorDefinition) => !excludedConnectorIds.includes(Connector.id(connectorDefinition))
    );
  }, [connectionDefinitions, workspace.workspaceId]);

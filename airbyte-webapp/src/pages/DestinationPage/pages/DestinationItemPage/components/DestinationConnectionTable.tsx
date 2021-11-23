import React, { useCallback } from "react";
import { useResource } from "rest-hooks";

import { ConnectionTable } from "components/EntityTable";
import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import { Connection } from "core/resources/Connection";
import useSyncActions from "components/EntityTable/hooks";
import { getConnectionTableData } from "components/EntityTable/utils";
import { ITableDataItem } from "components/EntityTable/types";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  connections: Connection[];
};

const DestinationConnectionTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const { changeStatus, syncManualConnection } = useSyncActions();

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const data = getConnectionTableData(
    connections,
    sourceDefinitions,
    destinationDefinitions,
    "destination"
  );

  const onChangeStatus = useCallback(
    async (connectionId: string) => {
      const connection = connections.find(
        (item) => item.connectionId === connectionId
      );

      if (connection) {
        await changeStatus(connection);
      }
    },
    [changeStatus, connections]
  );

  const onSync = useCallback(
    async (connectionId: string) => {
      const connection = connections.find(
        (item) => item.connectionId === connectionId
      );
      if (connection) {
        await syncManualConnection(connection);
      }
    },
    [connections, syncManualConnection]
  );

  const clickRow = (source: ITableDataItem) =>
    push(`${Routes.Connections}/${source.connectionId}`);

  return (
    <ConnectionTable
      data={data}
      onClickRow={clickRow}
      entity="destination"
      onChangeStatus={onChangeStatus}
      onSync={onSync}
    />
  );
};

export default DestinationConnectionTable;

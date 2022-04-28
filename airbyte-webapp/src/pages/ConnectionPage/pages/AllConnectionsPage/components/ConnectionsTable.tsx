import React, { useCallback } from "react";

import { ConnectionTable } from "components/EntityTable";
import useSyncActions from "components/EntityTable/hooks";
import { ITableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { Connection } from "core/domain/connection";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

type IProps = {
  connections: Connection[];
};

const ConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const { changeStatus, syncManualConnection } = useSyncActions();

  const { sourceDefinitions } = useSourceDefinitionList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getConnectionTableData(connections, sourceDefinitions, destinationDefinitions, "connection");

  const onChangeStatus = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);

      if (connection) {
        await changeStatus(connection);
      }
    },
    [changeStatus, connections]
  );

  const onSync = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);
      if (connection) {
        await syncManualConnection(connection);
      }
    },
    [connections, syncManualConnection]
  );

  const clickRow = (source: ITableDataItem) => push(`${source.connectionId}`);

  return (
    <ConnectionTable
      data={data}
      onClickRow={clickRow}
      entity="connection"
      onChangeStatus={onChangeStatus}
      onSync={onSync}
    />
  );
};

export default ConnectionsTable;

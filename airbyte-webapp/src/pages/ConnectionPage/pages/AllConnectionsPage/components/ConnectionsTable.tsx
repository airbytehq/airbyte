import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { ConnectionTable } from "components/EntityTable";
import useSyncActions from "components/EntityTable/hooks";
import { ITableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";

interface IProps {
  connections: WebBackendConnectionListItem[];
}

const ConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const navigate = useNavigate();
  const { syncManualConnection } = useSyncActions();

  const data = getConnectionTableData(connections, "connection");

  const onSync = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);
      if (connection) {
        await syncManualConnection(connection);
      }
    },
    [connections, syncManualConnection]
  );

  const clickRow = (source: ITableDataItem) => navigate(`${source.connectionId}`);

  return <ConnectionTable data={data} onClickRow={clickRow} entity="connection" onSync={onSync} />;
};

export default ConnectionsTable;

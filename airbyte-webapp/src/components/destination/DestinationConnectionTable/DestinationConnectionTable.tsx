import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { ConnectionTable } from "components/EntityTable";
import useSyncActions from "components/EntityTable/hooks";
import { ITableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { RoutePaths } from "pages/routePaths";

import styles from "./DestinationConnectionTable.module.scss";

interface IProps {
  connections: WebBackendConnectionListItem[];
}

export const DestinationConnectionTable: React.FC<IProps> = ({ connections }) => {
  const navigate = useNavigate();
  const { syncManualConnection } = useSyncActions();

  const data = getConnectionTableData(connections, "destination");

  const onSync = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);
      if (connection) {
        await syncManualConnection(connection);
      }
    },
    [connections, syncManualConnection]
  );

  const clickRow = (source: ITableDataItem) => navigate(`../../../${RoutePaths.Connections}/${source.connectionId}`);

  return (
    <div className={styles.content}>
      <ConnectionTable data={data} onClickRow={clickRow} entity="destination" onSync={onSync} />
    </div>
  );
};

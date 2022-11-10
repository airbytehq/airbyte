import React, { useCallback } from "react";
import { useQueryClient } from "react-query";

import { ConnectionTable } from "components/EntityTable";
import useSyncActions from "components/EntityTable/hooks";
import { ITableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { invalidateConnectionsList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import { WebBackendConnectionRead } from "../../../../../core/request/AirbyteClient";

interface IProps {
  connections: WebBackendConnectionRead[];
}

const ConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const { changeStatus, syncManualConnection } = useSyncActions();
  const queryClient = useQueryClient();

  const { sourceDefinitions } = useSourceDefinitionList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getConnectionTableData(connections, sourceDefinitions, destinationDefinitions, "connection");

  // const data = [
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 1,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  //   {
  //     name: "Amazon Seller Partner ...",
  //     status: "Inactive",
  //     lastSync: 2,
  //     entityName: "Amazon Seller Partner",
  //     connectorName: "Snowflake",
  //     connectionId: "",
  //     lastSyncStatus: "1 hour ago",
  //     enabled: false,
  //   },
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 3,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  //   {
  //     name: "Amazon Seller Partner ...",
  //     status: "Inactive",
  //     lastSync: 4,
  //     entityName: "Amazon Seller Partner",
  //     connectorName: "Snowflake",
  //     connectionId: "",
  //     lastSyncStatus: "1 hour ago",
  //     enabled: false,
  //   },
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 5,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  // ];

  const onChangeStatus = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);

      if (connection) {
        await changeStatus(connection);
        await invalidateConnectionsList(queryClient);
      }
    },
    [changeStatus, connections, queryClient]
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

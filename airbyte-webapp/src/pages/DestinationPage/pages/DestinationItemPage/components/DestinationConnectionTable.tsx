import React, { useCallback } from "react";

import { ConnectionTable } from "components/EntityTable";
import useRouter from "hooks/useRouter";
import { Connection } from "core/domain/connection";
import useSyncActions from "components/EntityTable/hooks";
import { getConnectionTableData } from "components/EntityTable/utils";
import { ITableDataItem } from "components/EntityTable/types";
import { RoutePaths } from "pages/routePaths";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

type IProps = {
  connections: Connection[];
};

const DestinationConnectionTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const { changeStatus, syncManualConnection } = useSyncActions();

  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

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
    push(`../../${RoutePaths.Connections}/${source.connectionId}`);

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

import React, { useCallback } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import { useResource } from "rest-hooks";

import Table from "../../../../../components/Table";
import FrequencyCell from "./FrequencyCell";
import LastSyncCell from "./LastSyncCell";
import StatusCell from "./StatusCell";
import ConnectorCell from "./ConnectorCell";
import NameCell from "./NameCell";
import { Routes } from "../../../../routes";
import useRouter from "../../../../../components/hooks/useRouterHook";
import { Connection } from "../../../../../core/resources/Connection";
import config from "../../../../../config";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import DestinationImplementationResource from "../../../../../core/resources/DestinationImplementation";
import DestinationResource from "../../../../../core/resources/Destination";
import useConnection from "../../../../../components/hooks/services/useConnectionHook";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type IProps = {
  connections: Connection[];
};

type ITableDataItem = {
  connectionId: string;
  sourceId: string;
  name: string;
  schedule: string;
  lastSync: number;
  enabled: boolean;
  error: boolean;
};

const SourcesTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();

  const { updateConnection } = useConnection();
  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
  });

  const data = connections.map(item => ({
    connectionId: item.connectionId,
    name: item.source?.name,
    enabled: item.status === "active",
    sourceId: item.source?.sourceId,
    sourceName: item.source?.sourceName,
    schedule: item.schedule,
    lastSync: item.lastSync
  }));

  const onChangeStatus = useCallback(
    async (connectionId: string) => {
      const connection = connections.find(
        item => item.connectionId === connectionId
      );

      await updateConnection({
        connectionId,
        syncSchema: connection?.syncSchema,
        schedule: connection?.schedule || null,
        status: connection?.status === "active" ? "inactive" : "active"
      });

      const frequency = FrequencyConfig.find(
        item =>
          JSON.stringify(item.config) === JSON.stringify(connection?.schedule)
      );

      AnalyticsService.track("Source - Action", {
        user_id: config.ui.workspaceId,
        action:
          connection?.status === "active"
            ? "Disable connection"
            : "Reenable connection",
        connector_source: connection?.source?.sourceName,
        connector_source_id: connection?.source?.sourceId,
        connector_destination: destination.name,
        connector_destination_id: destination.destinationId,
        frequency: frequency?.text
      });
    },
    [connections, destination.destinationId, destination.name, updateConnection]
  );

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="sources.name" />,
        headerHighlighted: true,
        accessor: "name",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <NameCell
            value={cell.value}
            error={row.original.error}
            enabled={row.original.enabled}
          />
        )
      },
      {
        Header: <FormattedMessage id="sources.connector" />,
        accessor: "sourceName",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} />
        )
      },
      {
        Header: <FormattedMessage id="sources.frequency" />,
        accessor: "schedule",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <FrequencyCell value={cell.value} enabled={row.original.enabled} />
        )
      },
      {
        Header: <FormattedMessage id="sources.lastSync" />,
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell
            timeInSecond={cell.value}
            enabled={row.original.enabled}
          />
        )
      },
      {
        Header: <FormattedMessage id="sources.enabled" />,
        accessor: "enabled",
        collapse: true,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <StatusCell
            enabled={cell.value}
            error={row.original.error}
            connectionId={row.original.connectionId}
            onChangeStatus={onChangeStatus}
          />
        )
      }
    ],
    [onChangeStatus]
  );

  const clickRow = (connection: any) =>
    push(`${Routes.Source}/${connection.connectionId}`);

  return (
    <Content>
      <Table columns={columns} data={data} onClickRow={clickRow} erroredRows />
    </Content>
  );
};

export default SourcesTable;

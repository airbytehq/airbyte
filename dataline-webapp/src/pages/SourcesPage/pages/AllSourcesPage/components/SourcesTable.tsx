import React from "react";
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
import ConnectionResource from "../../../../../core/resources/Connection";
import config from "../../../../../config";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type ITableDataItem = {
  name: string;
  connector: string;
  frequency: string;
  date: number;
  enabled: boolean;
  error: boolean;
};

const SourcesTable: React.FC = () => {
  const { push } = useRouter();
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  // TODO: add real data for table
  const data = connections.map(item => ({
    connectionId: item.connectionId,
    name: item.name,
    connector: "TEST data",
    frequency: "manual",
    date: 1597693584000,
    enabled: true,
    error: false
  }));

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
        accessor: "connector",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} />
        )
      },
      {
        Header: <FormattedMessage id="sources.frequency" />,
        accessor: "frequency",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <FrequencyCell value={cell.value} enabled={row.original.enabled} />
        )
      },
      {
        Header: <FormattedMessage id="sources.lastSync" />,
        accessor: "date",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell value={cell.value} enabled={row.original.enabled} />
        )
      },
      {
        Header: <FormattedMessage id="sources.enabled" />,
        accessor: "enabled",
        collapse: true,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <StatusCell enabled={cell.value} error={row.original.error} />
        )
      }
    ],
    []
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

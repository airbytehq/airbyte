import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import Table from "components/Table";

import LastSyncCell from "./components/LastSyncCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import FrequencyCell from "./components/FrequencyCell";
import StatusCell from "./components/StatusCell";
import { ITableDataItem } from "./types";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type IProps = {
  data: ITableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: ITableDataItem) => void;
  onChangeStatus: (id: string) => void;
  onSync: (id: string) => void;
};

const ConnectionTable: React.FC<IProps> = ({
  data,
  entity,
  onClickRow,
  onChangeStatus,
  onSync,
}) => {
  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id={`tables.${entity}ConnectionToName`} />,
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <NameCell
            value={cell.value}
            enabled={row.original.enabled}
            status={row.original.lastSyncStatus}
          />
        ),
      },
      {
        Header: <FormattedMessage id="tables.connector" />,
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} />
        ),
      },

      {
        Header: <FormattedMessage id="tables.frequency" />,
        accessor: "schedule",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <FrequencyCell value={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="tables.lastSync" />,
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell
            timeInSecond={cell.value}
            enabled={row.original.enabled}
          />
        ),
      },
      {
        Header: <FormattedMessage id="tables.enabled" />,
        accessor: "enabled",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <StatusCell
            enabled={cell.value}
            id={row.original.connectionId}
            isSyncing={row.original.isSyncing}
            isManual={!row.original.schedule}
            onChangeStatus={onChangeStatus}
            onSync={onSync}
          />
        ),
      },
    ],
    [entity, onChangeStatus, onSync]
  );

  return (
    <Content>
      <Table
        columns={columns}
        data={data}
        onClickRow={onClickRow}
        erroredRows
      />
    </Content>
  );
};

export default ConnectionTable;

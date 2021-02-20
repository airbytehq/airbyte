import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import Table from "../Table";
import LastSyncCell from "./components/LastSyncCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type ITableDataItem = {
  entityId: string;
  entityName: string;
  connectorName: string;
  connectEntities: {
    name: string;
    connector: string;
  }[];
  enabled: boolean;
  lastSync?: number | null;
};

type IProps = {
  data: ITableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: object) => void;
};

const ImplementationTable: React.FC<IProps> = ({
  data,
  entity,
  onClickRow,
}) => {
  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="tables.name" />,
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <NameCell value={cell.value} enabled={row.original.enabled} />
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
        Header: <FormattedMessage id={`tables.${entity}ConnectWith`} />,
        accessor: "connectEntities",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectEntitiesCell
            values={cell.value}
            entity={entity}
            enabled={row.original.enabled}
          />
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
    ],
    [entity]
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

export default ImplementationTable;

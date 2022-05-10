import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import Table from "components/Table";

import AllConnectionsStatusCell from "./components/AllConnectionsStatusCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";
import ConnectorCell from "./components/ConnectorCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import { EntityTableDataItem } from "./types";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type IProps = {
  data: EntityTableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: EntityTableDataItem) => void;
};

const ImplementationTable: React.FC<IProps> = ({ data, entity, onClickRow }) => {
  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="tables.name" />,
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <NameCell value={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="tables.connector" />,
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} img={row.original.connectorIcon} />
        ),
      },
      {
        Header: <FormattedMessage id={`tables.${entity}ConnectWith`} />,
        accessor: "connectEntities",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectEntitiesCell values={cell.value} entity={entity} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="tables.lastSync" />,
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <LastSyncCell timeInSecond={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="sources.status" />,
        id: "status",
        accessor: "connectEntities",
        Cell: ({ cell }: CellProps<EntityTableDataItem>) => <AllConnectionsStatusCell connectEntities={cell.value} />,
      },
    ],
    [entity]
  );

  return (
    <Content>
      <Table columns={columns} data={data} onClickRow={onClickRow} erroredRows />
    </Content>
  );
};

export default ImplementationTable;

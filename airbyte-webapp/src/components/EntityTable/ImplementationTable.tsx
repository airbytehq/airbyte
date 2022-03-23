import React, { useCallback } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import queryString from "query-string";

import Table from "components/Table";

import LastSyncCell from "./components/LastSyncCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";
import { EntityTableDataItem, SortOrderEnum } from "./types";
import AllConnectionsStatusCell from "./components/AllConnectionsStatusCell";
import useRouter from "hooks/useRouter";
import SortButton from "./components/SortButton";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

type IProps = {
  data: EntityTableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: EntityTableDataItem) => void;
};

const ImplementationTable: React.FC<IProps> = ({
  data,
  entity,
  onClickRow,
}) => {
  const { query, push } = useRouter();
  const sortBy = query.sortBy || "entity";
  const sortOrder = query.order || SortOrderEnum.ASC;

  const onSortClick = useCallback(
    (field: string) => {
      const order =
        sortBy !== field
          ? SortOrderEnum.ASC
          : sortOrder === SortOrderEnum.ASC
          ? SortOrderEnum.DESC
          : SortOrderEnum.ASC;
      push({
        search: queryString.stringify(
          {
            sortBy: field,
            order: order,
          },
          { skipNull: true }
        ),
      });
    },
    [push, sortBy, sortOrder]
  );

  const sortData = useCallback(
    (a, b) => {
      const result = a[`${sortBy}Name`]
        .toLowerCase()
        .localeCompare(b[`${sortBy}Name`].toLowerCase());

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const sortingData = React.useMemo(() => data.sort(sortData), [
    sortData,
    data,
  ]);

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <>
            <FormattedMessage id="tables.name" />
            <SortButton
              wasActive={sortBy === "entity"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("entity")}
            />
          </>
        ),
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <NameCell value={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: (
          <>
            <FormattedMessage id="tables.connector" />
            <SortButton
              wasActive={sortBy === "connector"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("connector")}
            />
          </>
        ),
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectorCell
            value={cell.value}
            enabled={row.original.enabled}
            img={row.original.connectorIcon}
          />
        ),
      },
      {
        Header: (
          <>
            <FormattedMessage id={`tables.${entity}ConnectWith`} />
            <SortButton
              wasActive={sortBy === "destination"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("destination")}
            />
          </>
        ),
        accessor: "connectEntities",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
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
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <LastSyncCell
            timeInSecond={cell.value}
            enabled={row.original.enabled}
          />
        ),
      },
      {
        Header: <FormattedMessage id="sources.status" />,
        id: "status",
        accessor: "connectEntities",
        Cell: ({ cell }: CellProps<EntityTableDataItem>) => (
          <AllConnectionsStatusCell connectEntities={cell.value} />
        ),
      },
    ],
    [entity, onSortClick, sortBy, sortOrder]
  );

  return (
    <Content>
      <Table
        columns={columns}
        data={sortingData}
        onClickRow={onClickRow}
        erroredRows
      />
    </Content>
  );
};

export default ImplementationTable;

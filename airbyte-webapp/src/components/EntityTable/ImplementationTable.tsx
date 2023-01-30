import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import { CellProps } from "react-table";

import { Table, SortableTableHeader } from "components/ui/Table";

import { useQuery } from "hooks/useQuery";

import AllConnectionsStatusCell from "./components/AllConnectionsStatusCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";
import { ConnectorNameCell } from "./components/ConnectorNameCell";
import { EntityNameCell } from "./components/EntityNameCell";
import { LastSyncCell } from "./components/LastSyncCell";
import styles from "./ImplementationTable.module.scss";
import { EntityTableDataItem, SortOrderEnum } from "./types";

interface IProps {
  data: EntityTableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: EntityTableDataItem) => void;
}

const ImplementationTable: React.FC<IProps> = ({ data, entity, onClickRow }) => {
  const query = useQuery<{ sortBy?: string; order?: SortOrderEnum }>();
  const navigate = useNavigate();
  const sortBy = query.sortBy || "entity";
  const sortOrder = query.order || SortOrderEnum.ASC;

  const onSortClick = useCallback(
    (field: string) => {
      const order =
        sortBy !== field ? SortOrderEnum.ASC : sortOrder === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;
      navigate({
        search: queryString.stringify(
          {
            sortBy: field,
            order,
          },
          { skipNull: true }
        ),
      });
    },
    [navigate, sortBy, sortOrder]
  );

  const sortData = useCallback(
    (a, b) => {
      let result;
      if (sortBy === "lastSync") {
        result = b[sortBy] - a[sortBy];
      } else {
        result = a[`${sortBy}Name`].toLowerCase().localeCompare(b[`${sortBy}Name`].toLowerCase());
      }

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const sortingData = React.useMemo(() => data.sort(sortData), [sortData, data]);
  const columns = React.useMemo(
    () => [
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("entity")}
            isActive={sortBy === "entity"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.name" />
          </SortableTableHeader>
        ),
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <EntityNameCell value={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("connector")}
            isActive={sortBy === "connector"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.connector" />
          </SortableTableHeader>
        ),
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectorNameCell value={cell.value} icon={row.original.connectorIcon} enabled={row.original.enabled} />
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
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("lastSync")}
            isActive={sortBy === "lastSync"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.lastSync" />
          </SortableTableHeader>
        ),
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
    [entity, onSortClick, sortBy, sortOrder]
  );

  return (
    <div className={styles.content}>
      <Table columns={columns} data={sortingData} onClickRow={onClickRow} erroredRows testId={`${entity}sTable`} />
    </div>
  );
};

export default ImplementationTable;

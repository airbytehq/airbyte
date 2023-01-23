import { ColumnDef } from "@tanstack/react-table";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { NextTable } from "components/ui/NextTable";
import { SortableTableHeader } from "components/ui/Table";

import { useQuery } from "hooks/useQuery";

import AllConnectionsStatusCell from "./components/AllConnectionsStatusCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";
import ConnectorCell from "./components/ConnectorCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import styles from "./ImplementationTable.module.scss";
import { EntityTableDataItem, SortOrderEnum } from "./types";

interface IProps {
  data: EntityTableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: EntityTableDataItem) => void;
}

interface AllConnectionStatusConnectEntity {
  name: string;
  connector: string;
  status: string;
  lastSyncStatus: string;
}

type ColumnDefs = [
  ColumnDef<EntityTableDataItem, string>,
  ColumnDef<EntityTableDataItem, string>,
  ColumnDef<EntityTableDataItem, AllConnectionStatusConnectEntity[]>,
  ColumnDef<EntityTableDataItem, number | null>,
  ColumnDef<EntityTableDataItem, AllConnectionStatusConnectEntity[]>
];

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
  const columns = React.useMemo<ColumnDefs>(
    () => [
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("entity")}
            isActive={sortBy === "entity"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.name" />
          </SortableTableHeader>
        ),
        meta: {
          thClassName: styles.thEntityName,
          headerHighlighted: true,
        },
        accessorKey: "entityName",
        cell: (props) => <NameCell value={props.cell.getValue()} enabled={props.row.original.enabled} />,
      },
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("connector")}
            isActive={sortBy === "connector"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.connector" />
          </SortableTableHeader>
        ),
        accessorKey: "connectorName",
        cell: (props) => (
          <ConnectorCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            img={props.row.original.connectorIcon}
          />
        ),
      },
      {
        header: () => <FormattedMessage id={`tables.${entity}ConnectWith`} />,
        accessorKey: "connectEntities",
        cell: (props) => (
          <ConnectEntitiesCell values={props.cell.getValue()} entity={entity} enabled={props.row.original.enabled} />
        ),
      },
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("lastSync")}
            isActive={sortBy === "lastSync"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.lastSync" />
          </SortableTableHeader>
        ),
        accessorKey: "lastSync",
        cell: (props) => (
          <LastSyncCell timeInSecond={props.cell.getValue() || 0} enabled={props.row.original.enabled} />
        ),
      },
      {
        header: () => <FormattedMessage id="sources.status" />,
        id: "status",
        accessorKey: "connectEntities",
        cell: (props) => <AllConnectionsStatusCell connectEntities={props.cell.getValue()} />,
      },
    ],
    [entity, onSortClick, sortBy, sortOrder]
  );

  return (
    <div className={styles.content}>
      <NextTable columns={columns} data={sortingData} onClickRow={onClickRow} erroredRows testId={`${entity}sTable`} />
    </div>
  );
};

export default ImplementationTable;

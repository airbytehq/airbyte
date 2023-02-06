import { createColumnHelper } from "@tanstack/react-table";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { NextTable } from "components/ui/NextTable";
import { SortableTableHeader } from "components/ui/Table";

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

  const columnHelper = createColumnHelper<EntityTableDataItem>();

  const columns = React.useMemo(
    () => [
      columnHelper.accessor("entityName", {
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
        },
        cell: (props) => <EntityNameCell value={props.cell.getValue()} enabled={props.row.original.enabled} />,
      }),
      columnHelper.accessor("connectorName", {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("connector")}
            isActive={sortBy === "connector"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.connector" />
          </SortableTableHeader>
        ),
        cell: (props) => (
          <ConnectorNameCell
            value={props.cell.getValue()}
            icon={props.row.original.connectorIcon}
            enabled={props.row.original.enabled}
          />
        ),
      }),
      columnHelper.accessor("connectEntities", {
        header: () => <FormattedMessage id={`tables.${entity}ConnectWith`} />,
        cell: (props) => (
          <ConnectEntitiesCell values={props.cell.getValue()} entity={entity} enabled={props.row.original.enabled} />
        ),
      }),
      columnHelper.accessor("lastSync", {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("lastSync")}
            isActive={sortBy === "lastSync"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.lastSync" />
          </SortableTableHeader>
        ),
        cell: (props) => (
          <LastSyncCell timeInSeconds={props.cell.getValue() || 0} enabled={props.row.original.enabled} />
        ),
      }),
      columnHelper.accessor("connectEntities", {
        header: () => <FormattedMessage id="sources.status" />,
        id: "status",
        cell: (props) => <AllConnectionsStatusCell connectEntities={props.cell.getValue()} />,
      }),
    ],
    [columnHelper, entity, onSortClick, sortBy, sortOrder]
  );

  return (
    <div className={styles.content}>
      <NextTable columns={columns} data={sortingData} onClickRow={onClickRow} testId={`${entity}sTable`} />
    </div>
  );
};

export default ImplementationTable;

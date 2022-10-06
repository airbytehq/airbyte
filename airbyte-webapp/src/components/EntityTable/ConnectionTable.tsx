import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import { CellProps } from "react-table";

import { Table } from "components/ui/Table";

import { ConnectionScheduleType } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useQuery } from "hooks/useQuery";

import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import FrequencyCell from "./components/FrequencyCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import SortIcon from "./components/SortIcon";
import StatusCell from "./components/StatusCell";
import styles from "./ConnectionTable.module.scss";
import { ITableDataItem, SortOrderEnum } from "./types";

interface IProps {
  data: ITableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ITableDataItem) => void;
  onSync: (id: string) => void;
}

const ConnectionTable: React.FC<IProps> = ({ data, entity, onClickRow, onSync }) => {
  const navigate = useNavigate();
  const query = useQuery<{ sortBy?: string; order?: SortOrderEnum }>();
  const allowSync = useFeature(FeatureItem.AllowSync);

  const sortBy = query.sortBy || "entityName";
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
        result = a[sortBy].toLowerCase().localeCompare(b[sortBy].toLowerCase());
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
          <button className={styles.tableHeaderButton} onClick={() => onSortClick("name")}>
            <FormattedMessage id="tables.name" />
            <SortIcon wasActive={sortBy === "name"} lowToLarge={sortOrder === SortOrderEnum.ASC} />
          </button>
        ),
        headerHighlighted: true,
        accessor: "name",
        customWidth: 30,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <NameCell value={cell.value} enabled={row.original.enabled} status={row.original.lastSyncStatus} />
        ),
      },
      {
        Header: (
          <button className={styles.tableHeaderButton} onClick={() => onSortClick("entityName")}>
            {entity === "connection" ? (
              <FormattedMessage id="tables.destinationConnectionToName" />
            ) : (
              <FormattedMessage id={`tables.${entity}ConnectionToName`} />
            )}
            <SortIcon wasActive={sortBy === "entityName"} lowToLarge={sortOrder === SortOrderEnum.ASC} />
          </button>
        ),
        headerHighlighted: true,
        accessor: "entityName",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <NameCell
            value={cell.value}
            enabled={row.original.enabled}
            icon={entity === "connection"}
            img={row.original.entityIcon}
          />
        ),
      },
      {
        Header: (
          <button className={styles.tableHeaderButton} onClick={() => onSortClick("connectorName")}>
            {entity === "connection" ? (
              <FormattedMessage id="tables.sourceConnectionToName" />
            ) : (
              <FormattedMessage id="tables.connector" />
            )}
            <SortIcon wasActive={sortBy === "connectorName"} lowToLarge={sortOrder === SortOrderEnum.ASC} />
          </button>
        ),
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} img={row.original.connectorIcon} />
        ),
      },

      {
        Header: <FormattedMessage id="tables.frequency" />,
        accessor: "scheduleData",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <FrequencyCell value={cell.value} enabled={row.original.enabled} scheduleType={row.original.scheduleType} />
        ),
      },
      {
        Header: (
          <button className={styles.tableHeaderButton} onClick={() => onSortClick("lastSync")}>
            <FormattedMessage id="tables.lastSync" />
            <SortIcon wasActive={sortBy === "lastSync"} lowToLarge={sortOrder === SortOrderEnum.ASC} />
          </button>
        ),
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell timeInSecond={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="tables.enabled" />,
        accessor: "enabled",
        customWidth: 1,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <StatusCell
            enabled={cell.value}
            id={row.original.connectionId}
            isSyncing={row.original.isSyncing}
            isManual={row.original.scheduleType === ConnectionScheduleType.manual}
            onSync={onSync}
            allowSync={allowSync}
          />
        ),
      },
      {
        Header: "",
        accessor: "connectionId",
        customWidth: 1,
        Cell: ({ cell }: CellProps<ITableDataItem>) => <ConnectionSettingsCell id={cell.value} />,
      },
    ],
    [allowSync, entity, onSync, onSortClick, sortBy, sortOrder]
  );

  return <Table columns={columns} data={sortingData} onClickRow={onClickRow} erroredRows />;
};

export default ConnectionTable;

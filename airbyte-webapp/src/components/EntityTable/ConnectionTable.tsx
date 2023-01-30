import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import { CellProps } from "react-table";

import { Table, SortableTableHeader } from "components/ui/Table";

import { ConnectionScheduleType, SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useQuery } from "hooks/useQuery";

import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import { ConnectionStatusCell } from "./components/ConnectionStatusCell";
import { ConnectorNameCell } from "./components/ConnectorNameCell";
import { FrequencyCell } from "./components/FrequencyCell";
import { LastSyncCell } from "./components/LastSyncCell";
import { StatusCell } from "./components/StatusCell";
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
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);
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
          <SortableTableHeader
            onClick={() => onSortClick("name")}
            isActive={sortBy === "name"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.name" />
          </SortableTableHeader>
        ),
        headerHighlighted: true,
        accessor: "name",
        customWidth: 30,
        responsive: true,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectionStatusCell
            status={row.original.lastSyncStatus}
            value={cell.value}
            enabled={row.original.enabled}
          />
        ),
      },
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("entityName")}
            isActive={sortBy === "entityName"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage
              id={entity === "connection" ? "tables.destinationConnectionToName" : `tables.${entity}ConnectionToName`}
            />
          </SortableTableHeader>
        ),
        headerHighlighted: true,
        accessor: "entityName",
        customWidth: 30,
        responsive: true,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorNameCell value={cell.value} icon={row.original.entityIcon} enabled={row.original.enabled} />
        ),
      },
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("connectorName")}
            isActive={sortBy === "connectorName"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id={entity === "connection" ? "tables.sourceConnectionToName" : "tables.connector"} />
          </SortableTableHeader>
        ),
        accessor: "connectorName",
        customWidth: 30,
        responsive: true,
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <ConnectorNameCell value={cell.value} icon={row.original.connectorIcon} enabled={row.original.enabled} />
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
          <SortableTableHeader
            onClick={() => onSortClick("lastSync")}
            isActive={sortBy === "lastSync"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.lastSync" />
          </SortableTableHeader>
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
            schemaChange={row.original.schemaChange}
            enabled={cell.value}
            id={row.original.connectionId}
            isSyncing={row.original.isSyncing}
            isManual={row.original.scheduleType === ConnectionScheduleType.manual}
            onSync={onSync}
            hasBreakingChange={allowAutoDetectSchema && row.original.schemaChange === SchemaChange.breaking}
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
    [sortBy, sortOrder, entity, onSortClick, onSync, allowSync, allowAutoDetectSchema]
  );

  return <Table columns={columns} data={sortingData} onClickRow={onClickRow} erroredRows testId="connectionsTable" />;
};

export default ConnectionTable;

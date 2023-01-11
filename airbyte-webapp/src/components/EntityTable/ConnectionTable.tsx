import { CellContext, ColumnDef } from "@tanstack/react-table";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { SortableTableHeader } from "components/ui/Table";

import { ConnectionScheduleData, ConnectionScheduleType, SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useQuery } from "hooks/useQuery";

import { NextTable } from "../ui/NextTable";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import FrequencyCell from "./components/FrequencyCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import { StatusCell } from "./components/StatusCell";
import { ITableDataItem, SortOrderEnum } from "./types";

interface IProps {
  data: ITableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ITableDataItem) => void;
  onSync: (id: string) => void;
}

type ColumnDefs = [
  ColumnDef<ITableDataItem, string>,
  ColumnDef<ITableDataItem, string>,
  ColumnDef<ITableDataItem, string>,
  ColumnDef<ITableDataItem, ConnectionScheduleData>,
  ColumnDef<ITableDataItem, number>,
  ColumnDef<ITableDataItem, boolean>,
  ColumnDef<ITableDataItem, string>
];

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

  const columns = React.useMemo<ColumnDefs>(
    () => [
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("name")}
            isActive={sortBy === "name"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="tables.name" />
          </SortableTableHeader>
        ),
        meta: {
          headerHighlighted: true,
          customWidth: 30,
        },
        accessorKey: "name",
        cell: (props: CellContext<ITableDataItem, string>) => (
          <NameCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            status={props.row.original.lastSyncStatus}
          />
        ),
      },
      {
        header: () => (
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
        meta: {
          headerHighlighted: true,
        },
        accessorKey: "entityName",
        cell: (props: CellContext<ITableDataItem, string>) => (
          <NameCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            icon={entity === "connection"}
            img={props.row.original.entityIcon}
          />
        ),
      },
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("connectorName")}
            isActive={sortBy === "connectorName"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id={entity === "connection" ? "tables.sourceConnectionToName" : "tables.connector"} />
          </SortableTableHeader>
        ),
        accessorKey: "connectorName",
        cell: (props: CellContext<ITableDataItem, string>) => (
          <ConnectorCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            img={props.row.original.connectorIcon}
          />
        ),
      },
      {
        header: () => <FormattedMessage id="tables.frequency" />,
        accessorKey: "scheduleData",
        cell: (props: CellContext<ITableDataItem, ConnectionScheduleData>) => (
          <FrequencyCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            scheduleType={props.row.original.scheduleType}
          />
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
        cell: (props: CellContext<ITableDataItem, number>) => (
          <LastSyncCell timeInSecond={props.cell.getValue()} enabled={props.row.original.enabled} />
        ),
      },
      {
        header: () => <FormattedMessage id="tables.enabled" />,
        accessorKey: "enabled",
        meta: {
          customWidth: 1,
        },
        cell: (props: CellContext<ITableDataItem, boolean>) => (
          <StatusCell
            schemaChange={props.row.original.schemaChange}
            enabled={props.cell.getValue()}
            id={props.row.original.connectionId}
            isSyncing={props.row.original.isSyncing}
            isManual={props.row.original.scheduleType === ConnectionScheduleType.manual}
            onSync={onSync}
            hasBreakingChange={allowAutoDetectSchema && props.row.original.schemaChange === SchemaChange.breaking}
            allowSync={allowSync}
          />
        ),
      },
      {
        header: "",
        accessorKey: "connectionId",
        meta: {
          customWidth: 1,
        },
        cell: (props: CellContext<ITableDataItem, string>) => <ConnectionSettingsCell id={props.cell.getValue()} />,
      },
    ],
    [sortBy, sortOrder, entity, onSortClick, onSync, allowSync, allowAutoDetectSchema]
  );

  return <NextTable columns={columns} data={sortingData} onClickRow={onClickRow} erroredRows />;
};

export default ConnectionTable;

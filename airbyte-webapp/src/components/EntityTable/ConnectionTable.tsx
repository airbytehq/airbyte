import { createColumnHelper } from "@tanstack/react-table";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { SortableTableHeader } from "components/ui/Table";

import { ConnectionScheduleType, SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useQuery } from "hooks/useQuery";

import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import { ConnectionStatusCell } from "./components/ConnectionStatusCell";
import { ConnectorNameCell } from "./components/ConnectorNameCell";
import { FrequencyCell } from "./components/FrequencyCell";
import { LastSyncCell } from "./components/LastSyncCell";
import { StatusCell } from "./components/StatusCell";
import styles from "./ConnectionTable.module.scss";
import { ConnectionTableDataItem, SortOrderEnum } from "./types";
import { NextTable } from "../ui/NextTable";

interface ConnectionTableProps {
  data: ConnectionTableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ConnectionTableDataItem) => void;
}

const ConnectionTable: React.FC<ConnectionTableProps> = ({ data, entity, onClickRow }) => {
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

  const columnHelper = createColumnHelper<ConnectionTableDataItem>();

  const columns = React.useMemo(
    () => [
      columnHelper.accessor("name", {
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
          thClassName: styles.width30,
          responsive: true,
        },
        cell: (props) => (
          <ConnectionStatusCell
            status={props.row.original.lastSyncStatus}
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
          />
        ),
      }),
      columnHelper.accessor("entityName", {
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
          thClassName: styles.width30,
          responsive: true,
        },
        cell: (props) => (
          <ConnectorNameCell
            value={props.cell.getValue()}
            icon={props.row.original.entityIcon}
            enabled={props.row.original.enabled}
          />
        ),
      }),
      columnHelper.accessor("connectorName", {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("connectorName")}
            isActive={sortBy === "connectorName"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id={entity === "connection" ? "tables.sourceConnectionToName" : "tables.connector"} />
          </SortableTableHeader>
        ),
        meta: {
          thClassName: styles.width30,
          responsive: true,
        },
        cell: (props) => (
          <ConnectorNameCell
            value={props.cell.getValue()}
            icon={props.row.original.connectorIcon}
            enabled={props.row.original.enabled}
          />
        ),
      }),
      columnHelper.accessor("scheduleData", {
        header: () => <FormattedMessage id="tables.frequency" />,
        cell: (props) => (
          <FrequencyCell
            value={props.cell.getValue()}
            enabled={props.row.original.enabled}
            scheduleType={props.row.original.scheduleType}
          />
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
        cell: (props) => <LastSyncCell timeInSeconds={props.cell.getValue()} enabled={props.row.original.enabled} />,
      }),
      columnHelper.accessor("enabled", {
        header: () => <FormattedMessage id="tables.enabled" />,
        meta: {
          thClassName: styles.thEnabled,
        },
        cell: (props) => (
          <StatusCell
            schemaChange={props.row.original.schemaChange}
            enabled={props.cell.getValue()}
            id={props.row.original.connectionId}
            isSyncing={props.row.original.isSyncing}
            isManual={props.row.original.scheduleType === ConnectionScheduleType.manual}
            hasBreakingChange={allowAutoDetectSchema && props.row.original.schemaChange === SchemaChange.breaking}
            allowSync={allowSync}
          />
        ),
      }),
      columnHelper.accessor("connectionId", {
        header: "",
        meta: {
          thClassName: styles.thConnectionSettings,
        },
        cell: (props) => <ConnectionSettingsCell id={props.cell.getValue()} />,
      }),
    ],
    [columnHelper, sortBy, sortOrder, onSortClick, entity, allowAutoDetectSchema, allowSync]
  );

  return <NextTable columns={columns} data={sortingData} onClickRow={onClickRow} testId="connectionsTable" />;
};

export default ConnectionTable;

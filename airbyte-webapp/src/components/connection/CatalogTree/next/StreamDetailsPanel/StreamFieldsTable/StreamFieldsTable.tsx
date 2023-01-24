import { createColumnHelper } from "@tanstack/react-table";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { pathDisplayName } from "components/connection/CatalogTree/PathPopout";
import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { NextTable } from "components/ui/NextTable";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { equal } from "utils/objects";
import { getDataType } from "utils/useTranslateDataType";

import { ConnectorHeaderGroupIcon } from "./ConnectorHeaderGroupIcon";
import { CursorCell } from "./CursorCell";
import { PKCell } from "./PKCell";
import styles from "./StreamFieldsTable.module.scss";

export interface TableStream {
  path: string[];
  dataType: string;
  cursorDefined?: boolean;
  primaryKeyDefined?: boolean;
}

export interface StreamFieldsTableProps {
  config?: AirbyteStreamConfiguration;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  isCursorDefinitionSupported: boolean;
  isPKDefinitionSupported: boolean;
  syncSchemaFields: SyncSchemaField[];
}

export const StreamFieldsTable: React.FC<StreamFieldsTableProps> = ({
  config,
  onPkSelect,
  onCursorSelect,
  shouldDefineCursor,
  shouldDefinePk,
  isCursorDefinitionSupported,
  isPKDefinitionSupported,
  syncSchemaFields,
}) => {
  const { formatMessage } = useIntl();

  const isCursor = useMemo(() => (path: string[]) => equal(config?.cursorField, path), [config?.cursorField]);
  const isPrimaryKey = useMemo(
    () => (path: string[]) => !!config?.primaryKey?.some((p) => equal(p, path)),
    [config?.primaryKey]
  );

  // header group icons:
  const {
    connection: { source, destination },
  } = useConnectionFormService();

  // prepare data for table
  const tableData: TableStream[] = useMemo(
    () =>
      syncSchemaFields.map((stream) => ({
        path: stream.path,
        dataType: getDataType(stream),
        cursorDefined: shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(stream),
        primaryKeyDefined: shouldDefinePk && SyncSchemaFieldObject.isPrimitive(stream),
      })),
    [shouldDefineCursor, shouldDefinePk, syncSchemaFields]
  );

  const columnHelper = createColumnHelper<TableStream>();

  const sourceColumns = useMemo(
    () => [
      columnHelper.accessor("path", {
        id: "sourcePath",
        header: () => <FormattedMessage id="form.field.name" />,
        cell: ({ getValue }) => pathDisplayName(getValue()),
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.textCell,
        },
      }),
      columnHelper.accessor("dataType", {
        id: "sourceDataType",
        header: () => <FormattedMessage id="form.field.dataType" />,
        cell: ({ getValue }) => (
          <FormattedMessage id={`${getValue()}`} defaultMessage={formatMessage({ id: "airbyte.datatype.unknown" })} />
        ),
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.dataTypeCell,
        },
      }),
      columnHelper.accessor("cursorDefined", {
        id: "sourceCursorDefined",
        header: () => <FormattedMessage id="form.field.cursorField" />,
        cell: (props) => (
          <CursorCell
            isCursor={isCursor}
            isCursorDefinitionSupported={isCursorDefinitionSupported}
            onCursorSelect={onCursorSelect}
            {...props}
          />
        ),
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.cursorCell,
        },
      }),
      columnHelper.accessor("primaryKeyDefined", {
        id: "sourcePrimaryKeyDefined",
        header: () => <FormattedMessage id="form.field.primaryKey" />,
        cell: (props) => (
          <PKCell
            isPKDefinitionSupported={isPKDefinitionSupported}
            isPrimaryKey={isPrimaryKey}
            onPkSelect={onPkSelect}
            {...props}
          />
        ),

        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.pkCell,
        },
      }),
    ],
    [
      columnHelper,
      formatMessage,
      isCursor,
      isPrimaryKey,
      isCursorDefinitionSupported,
      isPKDefinitionSupported,
      onCursorSelect,
      onPkSelect,
    ]
  );

  const destinationColumns = useMemo(
    () => [
      columnHelper.accessor("path", {
        id: "destinationPath",
        header: () => <FormattedMessage id="form.field.name" />,
        cell: ({ getValue }) => pathDisplayName(getValue()),
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.textCell,
        },
      }),
    ],
    [columnHelper]
  );

  const columns = useMemo(
    () => [
      columnHelper.group({
        id: "source",
        header: () => <ConnectorHeaderGroupIcon type="source" icon={source.icon} />,
        columns: sourceColumns,
        meta: {
          thClassName: styles.headerGroupCell,
        },
      }),
      columnHelper.group({
        id: "arrow",
        header: () => <ArrowRightIcon />,
        columns: [
          {
            id: "_", // leave the column name empty
            cell: () => <ArrowRightIcon />,
            meta: {
              thClassName: styles.headerCell,
              tdClassName: styles.arrowCell,
            },
          },
        ],
        meta: {
          thClassName: styles.headerGroupCell,
        },
      }),
      columnHelper.group({
        id: "destination",
        header: () => <ConnectorHeaderGroupIcon type="destination" icon={destination.icon} />,
        columns: destinationColumns,
        meta: {
          thClassName: styles.headerGroupCell,
          tdClassName: styles.bodyCell,
        },
      }),
    ],
    [columnHelper, destination.icon, destinationColumns, source.icon, sourceColumns]
  );

  return <NextTable<TableStream> columns={columns} data={tableData} className={styles.customTableStyle} />;
};

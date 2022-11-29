import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { createColumnHelper } from "@tanstack/react-table";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { equal } from "utils/objects";
import { getDataType } from "utils/useTranslateDataType";

import { CheckBox } from "../../../../ui/CheckBox";
import { RadioButton } from "../../../../ui/RadioButton";
import { pathDisplayName } from "../../PathPopout";
import { NextTable } from "../NextTable";
import { ConnectorHeaderGroupIcon } from "./ConnectorHeaderGroupIcon";
import styles from "./StreamFieldsTable.module.scss";

interface TableStream {
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
  syncSchemaFields: SyncSchemaField[];
}

export const StreamFieldsTable: React.FC<StreamFieldsTableProps> = ({
  config,
  onPkSelect,
  onCursorSelect,
  shouldDefineCursor,
  shouldDefinePk,
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
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

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
        cell: ({ getValue, row }) => {
          return (
            getValue() && (
              <RadioButton checked={isCursor(row.original.path)} onChange={() => onCursorSelect(row.original.path)} />
            )
          );
        },
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.checkboxCell,
        },
      }),
      columnHelper.accessor("primaryKeyDefined", {
        id: "sourcePrimaryKeyDefined",
        header: () => <FormattedMessage id="form.field.primaryKey" />,
        cell: ({ getValue, row }) => {
          return (
            getValue() && (
              <CheckBox
                checked={isPrimaryKey(row.original.path)}
                onChange={() => onPkSelect(row.original.path)}
                className={styles.checkbox}
              />
            )
          );
        },
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.textCell,
        },
      }),
    ],
    [
      columnHelper,
      formatMessage,
      isCursor,
      isPrimaryKey,
      onCursorSelect,
      onPkSelect,
      shouldDefineCursor,
      shouldDefinePk,
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
      // In the design, but we may be unable to get the destination data type
      columnHelper.accessor("dataType", {
        id: "destinationDataType",
        header: () => <FormattedMessage id="form.field.dataType" />,
        cell: ({ getValue }) => (
          <FormattedMessage id={`${getValue()}`} defaultMessage={formatMessage({ id: "airbyte.datatype.unknown" })} />
        ),
        meta: {
          thClassName: styles.headerCell,
          tdClassName: styles.dataTypeCell,
        },
      }),
    ],
    [columnHelper, formatMessage]
  );

  const columns = useMemo(
    () => [
      columnHelper.group({
        id: "source",
        header: () => <ConnectorHeaderGroupIcon type="source" icon={sourceDefinition.icon} />,
        columns: sourceColumns,
        meta: {
          thClassName: styles.headerGroupCell,
        },
      }),
      columnHelper.group({
        id: "arrow",
        header: () => <FontAwesomeIcon icon={faArrowRight} />,
        columns: [
          {
            id: "_", // leave the column name empty
            cell: () => <FontAwesomeIcon icon={faArrowRight} />,
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
        header: () => <ConnectorHeaderGroupIcon type="destination" icon={destinationDefinition.icon} />,
        columns: destinationColumns,
        meta: {
          thClassName: styles.headerGroupCell,
          tdClassName: styles.bodyCell,
        },
      }),
    ],
    [columnHelper, destinationColumns, destinationDefinition.icon, sourceColumns, sourceDefinition.icon]
  );

  return <NextTable<TableStream> columns={columns} data={tableData} />;
};

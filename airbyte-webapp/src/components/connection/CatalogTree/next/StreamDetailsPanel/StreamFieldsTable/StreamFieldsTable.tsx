import { createColumnHelper } from "@tanstack/react-table";
import classNames from "classnames";
import isEqual from "lodash/isEqual";
import React, { useCallback, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { pathDisplayName } from "components/connection/CatalogTree/PathPopout";
import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { CheckBox } from "components/ui/CheckBox";
import { FlexContainer } from "components/ui/Flex";
import { NextTable } from "components/ui/NextTable";
import { Text } from "components/ui/Text";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useExperiment } from "hooks/services/Experiment";
import { getDataType } from "utils/useTranslateDataType";

import { ConnectorHeaderGroupIcon } from "./ConnectorHeaderGroupIcon";
import { CursorCell } from "./CursorCell";
import { PKCell } from "./PKCell";
import styles from "./StreamFieldsTable.module.scss";
import { SyncFieldCell } from "./SyncFieldCell";
import { CatalogTreeTableCell } from "../../CatalogTreeTableCell";

export interface TableStream {
  field: SyncSchemaField;
  isFieldSelected: boolean;
  path: string[];
  dataType: string;
  cursorDefined?: boolean;
  primaryKeyDefined?: boolean;
}

export interface StreamFieldsTableProps {
  config?: AirbyteStreamConfiguration;
  handleFieldToggle: (fieldPath: string[], isSelected: boolean) => void;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  isCursorDefinitionSupported: boolean;
  isPKDefinitionSupported: boolean;
  syncSchemaFields: SyncSchemaField[];
  toggleAllFieldsSelected: () => void;
}

export function isCursor(config: AirbyteStreamConfiguration | undefined, path: string[]): boolean {
  return config ? isEqual(config?.cursorField, path) : false;
}

export function isChildFieldCursor(config: AirbyteStreamConfiguration | undefined, path: string[]): boolean {
  return config?.cursorField ? isEqual([config.cursorField[0]], path) : false;
}

export function isPrimaryKey(config: AirbyteStreamConfiguration | undefined, path: string[]): boolean {
  return !!config?.primaryKey?.some((p) => isEqual(p, path));
}

export function isChildFieldPrimaryKey(config: AirbyteStreamConfiguration | undefined, path: string[]): boolean {
  return !!config?.primaryKey?.some((p) => isEqual([p[0]], path));
}

export const StreamFieldsTable: React.FC<StreamFieldsTableProps> = ({
  config,
  handleFieldToggle,
  onPkSelect,
  onCursorSelect,
  shouldDefineCursor,
  shouldDefinePk,
  isCursorDefinitionSupported,
  isPKDefinitionSupported,
  syncSchemaFields,
  toggleAllFieldsSelected,
}) => {
  const { formatMessage } = useIntl();
  const isColumnSelectionEnabled = useExperiment("connection.columnSelection", false);
  const checkIsCursor = useCallback((path: string[]) => isCursor(config, path), [config]);
  const checkIsChildFieldCursor = useCallback((path: string[]) => isChildFieldCursor(config, path), [config]);
  const checkIsPrimaryKey = useCallback((path: string[]) => isPrimaryKey(config, path), [config]);
  const checkIsChildFieldPrimaryKey = useCallback((path: string[]) => isChildFieldPrimaryKey(config, path), [config]);

  const checkIsFieldSelected = useCallback(
    (field: SyncSchemaField): boolean => {
      // All fields are implicitly selected if field selection is disabled
      if (!config?.fieldSelectionEnabled) {
        return true;
      }

      // path[0] is the top-level field name for all nested fields
      return !!config?.selectedFields?.find((f) => isEqual(f.fieldPath, [field.path[0]]));
    },
    [config]
  );

  // header group icons:
  const {
    connection: { source, destination },
    mode,
  } = useConnectionFormService();

  // prepare data for table
  const tableData: TableStream[] = useMemo(
    () =>
      syncSchemaFields.map((stream) => ({
        field: stream,
        isFieldSelected: checkIsFieldSelected(stream),
        path: stream.path,
        dataType: getDataType(stream),
        cursorDefined: shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(stream),
        primaryKeyDefined: shouldDefinePk && SyncSchemaFieldObject.isPrimitive(stream),
      })),
    [shouldDefineCursor, shouldDefinePk, syncSchemaFields, checkIsFieldSelected]
  );

  const columnHelper = createColumnHelper<TableStream>();

  const sourceColumns = useMemo(
    () => [
      ...(isColumnSelectionEnabled
        ? [
            columnHelper.display({
              id: "sourceSyncField",
              header: () => (
                <FlexContainer gap="md">
                  <CheckBox
                    checkboxSize="sm"
                    indeterminate={config?.fieldSelectionEnabled && !!config?.selectedFields?.length}
                    checked={!config?.fieldSelectionEnabled}
                    onChange={toggleAllFieldsSelected}
                    disabled={mode === "readonly"}
                  />
                  <FormattedMessage id="form.field.sync" />
                </FlexContainer>
              ),
              cell: (props) => (
                <SyncFieldCell
                  field={props.row.original.field}
                  isFieldSelected={props.row.original.isFieldSelected}
                  handleFieldToggle={handleFieldToggle}
                  checkIsCursor={checkIsCursor}
                  checkIsChildFieldCursor={checkIsChildFieldCursor}
                  checkIsPrimaryKey={checkIsPrimaryKey}
                  checkIsChildFieldPrimaryKey={checkIsChildFieldPrimaryKey}
                  syncMode={config?.syncMode}
                  destinationSyncMode={config?.destinationSyncMode}
                />
              ),
              meta: {
                thClassName: classNames(styles.headerCell, styles["headerCell--syncCell"]),
                tdClassName: styles.textCell,
              },
            }),
          ]
        : []),
      columnHelper.accessor("path", {
        id: "sourcePath",
        header: () => <FormattedMessage id="form.field.name" />,
        cell: ({ getValue }) => (
          <CatalogTreeTableCell size="small" withTooltip>
            <Text size="sm">{pathDisplayName(getValue())}</Text>
          </CatalogTreeTableCell>
        ),
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
            isCursor={checkIsCursor}
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
            isPrimaryKey={checkIsPrimaryKey}
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
      config?.fieldSelectionEnabled,
      config?.selectedFields?.length,
      formatMessage,
      handleFieldToggle,
      isColumnSelectionEnabled,
      checkIsCursor,
      checkIsChildFieldCursor,
      checkIsPrimaryKey,
      checkIsChildFieldPrimaryKey,
      isCursorDefinitionSupported,
      isPKDefinitionSupported,
      onCursorSelect,
      onPkSelect,
      toggleAllFieldsSelected,
      config?.syncMode,
      config?.destinationSyncMode,
      mode,
    ]
  );

  const destinationColumns = useMemo(
    () => [
      columnHelper.accessor("path", {
        id: "destinationPath",
        header: () => <FormattedMessage id="form.field.name" />,
        cell: ({ getValue }) => (
          <CatalogTreeTableCell size="small" withTooltip>
            <Text size="sm">{pathDisplayName(getValue())}</Text>
          </CatalogTreeTableCell>
        ),
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

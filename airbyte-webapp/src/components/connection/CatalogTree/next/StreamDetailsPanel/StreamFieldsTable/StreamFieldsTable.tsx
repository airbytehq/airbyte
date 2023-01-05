import { createColumnHelper } from "@tanstack/react-table";
import isEqual from "lodash/isEqual";
import React, { useCallback, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { pathDisplayName } from "components/connection/CatalogTree/PathPopout";
import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { CheckBox } from "components/ui/CheckBox";
import { FlexContainer } from "components/ui/Flex";
import { NextTable } from "components/ui/NextTable";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useExperiment } from "hooks/services/Experiment";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { equal } from "utils/objects";
import { getDataType } from "utils/useTranslateDataType";

import { ConnectorHeaderGroupIcon } from "./ConnectorHeaderGroupIcon";
import { CursorCell } from "./CursorCell";
import { PKCell } from "./PKCell";
import styles from "./StreamFieldsTable.module.scss";
import { SyncFieldCell } from "./SyncFieldCell";

export interface TableStream {
  sync: { isSelected: boolean; field: SyncSchemaField };
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
  const isCursor = useMemo(() => (path: string[]) => equal(config?.cursorField, path), [config?.cursorField]);
  const isPrimaryKey = useMemo(
    () => (path: string[]) => !!config?.primaryKey?.some((p) => equal(p, path)),
    [config?.primaryKey]
  );
  const isFieldSelected = useCallback(
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
  } = useConnectionFormService();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  // prepare data for table
  const tableData: TableStream[] = useMemo(
    () =>
      syncSchemaFields.map((stream) => ({
        sync: { field: stream, isSelected: isFieldSelected(stream), shouldDefinePk, shouldDefineCursor },
        path: stream.path,
        dataType: getDataType(stream),
        cursorDefined: shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(stream),
        primaryKeyDefined: shouldDefinePk && SyncSchemaFieldObject.isPrimitive(stream),
      })),
    [shouldDefineCursor, shouldDefinePk, syncSchemaFields, isFieldSelected]
  );

  const columnHelper = createColumnHelper<TableStream>();

  console.log(handleFieldToggle);

  const sourceColumns = useMemo(
    () => [
      ...(isColumnSelectionEnabled
        ? [
            columnHelper.accessor("sync", {
              id: "sourceSyncField",
              header: () => (
                <FlexContainer gap="md">
                  <CheckBox
                    checkboxSize="sm"
                    indeterminate={config?.fieldSelectionEnabled && !!config?.selectedFields?.length}
                    checked={!config?.fieldSelectionEnabled}
                    onClick={toggleAllFieldsSelected}
                  />
                  <FormattedMessage id="form.field.sync" />
                </FlexContainer>
              ),
              cell: ({ getValue }) => (
                <SyncFieldCell
                  {...getValue()}
                  handleFieldToggle={handleFieldToggle}
                  checkIsCursor={isCursor}
                  checkIsPrimaryKey={isPrimaryKey}
                  shouldDefineCursor={shouldDefineCursor}
                  shouldDefinePrimaryKey={shouldDefinePk}
                />
              ),
              meta: {
                thClassName: styles.headerCell,
                tdClassName: styles.textCell,
              },
            }),
          ]
        : []),
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
          tdClassName: styles.radioBtnCell,
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
          tdClassName: styles.textCell,
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
      isCursor,
      isPrimaryKey,
      isCursorDefinitionSupported,
      isPKDefinitionSupported,
      onCursorSelect,
      onPkSelect,
      shouldDefineCursor,
      shouldDefinePk,
      toggleAllFieldsSelected,
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
        header: () => <ConnectorHeaderGroupIcon type="source" icon={sourceDefinition.icon} />,
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

  return <NextTable<TableStream> columns={columns} data={tableData} className={styles.customTableStyle} />;
};

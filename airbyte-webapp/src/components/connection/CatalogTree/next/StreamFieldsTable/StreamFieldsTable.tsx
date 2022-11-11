import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { equal } from "utils/objects";
import { useTranslateDataType } from "utils/useTranslateDataType";

import { CheckBox } from "../../../../ui/CheckBox";
import { RadioButton } from "../../../../ui/RadioButton";
import { pathDisplayName } from "../../PathPopout";
import { NextTable } from "../NextTable";
import styles from "./StreamFieldsTable.module.scss";

export interface StreamFieldsTableProps {
  config?: AirbyteStreamConfiguration;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  syncSchemaFields: SyncSchemaField[];
}

// copied from StreamConnectionHeader
const renderIcon = (icon?: string): JSX.Element => <div className={styles.icon}>{getIcon(icon)}</div>;

export const StreamFieldsTable: React.FC<StreamFieldsTableProps> = ({
  config,
  onPkSelect,
  onCursorSelect,
  shouldDefineCursor,
  shouldDefinePk,
  syncSchemaFields,
}) => {
  const isCursor = useMemo(() => (path: string[]) => equal(config?.cursorField, path), [config?.cursorField]);
  const isPrimaryKey = useMemo(
    () => (path: string[]) => !!config?.primaryKey?.some((p) => equal(p, path)),
    [config?.primaryKey]
  );

  // header group icons:
  const {
    connection: { source, destination },
  } = useConnectionEditService();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const sourceColumns = useMemo(
    () => [
      {
        Header: <FormattedMessage id="form.field.name" />,
        headerClassName: styles.headerCell,
        accessor: "path",
        className: styles.textCell,
        Cell: ({ cell }: CellProps<SyncSchemaField>) => pathDisplayName(cell.value),
      },
      {
        Header: <FormattedMessage id="form.field.dataType" />,
        headerClassName: styles.headerCell,
        accessor: "dataType",
        className: styles.dataTypeCell,
        Cell: ({ row }: CellProps<SyncSchemaField>) => useTranslateDataType(row.original),
      },
      {
        Header: <>{shouldDefineCursor && <FormattedMessage id="form.field.cursorField" />}</>,
        headerClassName: styles.headerCell,
        accessor: "cursorField",
        className: styles.checkboxCell,
        Cell: ({ row }: CellProps<SyncSchemaField>) => {
          return (
            shouldDefineCursor &&
            SyncSchemaFieldObject.isPrimitive(row.original) && (
              <RadioButton checked={isCursor(row.original.path)} onChange={() => onCursorSelect(row.original.path)} />
            )
          );
        },
      },
      {
        Header: <FormattedMessage id="form.field.primaryKey" />,
        headerClassName: styles.headerCell,
        accessor: "primaryKey",
        className: styles.textCell,
        Cell: ({ row }: CellProps<SyncSchemaField>) => {
          return (
            shouldDefinePk &&
            SyncSchemaFieldObject.isPrimitive(row.original) && (
              <CheckBox checked={isPrimaryKey(row.original.path)} onChange={() => onPkSelect(row.original.path)} />
            )
          );
        },
      },
    ],
    [isCursor, isPrimaryKey, onCursorSelect, onPkSelect, shouldDefineCursor, shouldDefinePk]
  );

  const destinationColumns = useMemo(
    () => [
      {
        Header: <FormattedMessage id="form.field.name" />,
        headerClassName: styles.headerCell,
        accessor: "cleanedName",
        className: styles.textCell,
        Cell: ({ row }: CellProps<SyncSchemaField>) => row.original.cleanedName,
      },
      {
        // In the design, but we may be unable to get the destination data type
        Header: <FormattedMessage id="form.field.dataType" />,
        headerClassName: styles.headerCell,
        accessor: "format",
        className: styles.dataTypeCell,
        Cell: ({ row }: CellProps<SyncSchemaField>) => useTranslateDataType(row.original),
      },
    ],
    []
  );

  const columns = useMemo(
    () => [
      {
        Header: <div className={styles.connectorIconContainer}>{renderIcon(sourceDefinition.icon)} Source</div>,
        headerClassName: styles.headerGroupCell,
        id: "source icon",
        columns: sourceColumns,
      },
      {
        Header: <FontAwesomeIcon icon={faArrowRight} />,
        headerClassName: styles.headerGroupCell,
        id: "arrow",
        columns: [
          {
            accessor: "key",
            headerClassName: styles.headerCell,
            className: styles.arrowCell,
            Cell: () => <FontAwesomeIcon icon={faArrowRight} />,
          },
        ],
      },
      {
        Header: (
          <div className={styles.connectorIconContainer}>{renderIcon(destinationDefinition.icon)} Destination</div>
        ),
        headerClassName: styles.headerGroupCell,
        className: styles.bodyCell,
        id: "destination icon",
        columns: destinationColumns,
      },
    ],
    [sourceDefinition.icon, sourceColumns, destinationDefinition.icon, destinationColumns]
  );

  return <NextTable columns={columns} data={syncSchemaFields} light />;
};

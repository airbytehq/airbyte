import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { PropsWithChildren, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import { equal } from "../../../../../utils/objects";
import { useTranslateDataType } from "../../../../../utils/useTranslateDataType";
import { CheckBox } from "../../../../ui/CheckBox";
import { RadioButton } from "../../../../ui/RadioButton";
import { Table } from "../../../../ui/Table";
import DataTypeCell from "../../DataTypeCell";
import { pathDisplayName } from "../../PathPopout";
import styles from "./StreamFieldsTable.module.scss";

const HeaderCell: React.FC<PropsWithChildren<unknown>> = ({ children }) => (
  <div className={styles.headerCell}>{children}</div>
);

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
  const isCursor = useMemo(() => (path: string[]) => equal(config?.cursorField, path), [config?.cursorField]);
  const isPrimaryKey = useMemo(
    () => (path: string[]) => !!config?.primaryKey?.some((p) => equal(p, path)),
    [config?.primaryKey]
  );

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <HeaderCell>
            <FormattedMessage id="form.field.name" />
          </HeaderCell>
        ),
        accessor: "path",
        Cell: ({ cell }: CellProps<SyncSchemaField>) => pathDisplayName(cell.value),
      },
      {
        Header: (
          <HeaderCell>
            <FormattedMessage id="form.field.dataType" />
          </HeaderCell>
        ),
        accessor: "dataType",
        Cell: ({ row }: CellProps<SyncSchemaField>) => (
          <DataTypeCell>{useTranslateDataType(row.original)}</DataTypeCell>
        ),
      },
      {
        Header: <HeaderCell>{shouldDefineCursor && <FormattedMessage id="form.field.cursorField" />} </HeaderCell>,
        accessor: "cursorField",
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
        Header: (
          <HeaderCell>
            <FormattedMessage id="form.field.primaryKey" />
          </HeaderCell>
        ),
        accessor: "primaryKey",
        Cell: ({ row }: CellProps<SyncSchemaField>) => {
          return (
            shouldDefinePk &&
            SyncSchemaFieldObject.isPrimitive(row.original) && (
              <CheckBox checked={isPrimaryKey(row.original.path)} onChange={() => onPkSelect(row.original.path)} />
            )
          );
        },
      },
      {
        Header: (
          <HeaderCell>
            <FontAwesomeIcon icon={faArrowRight} />
          </HeaderCell>
        ),
        accessor: "key",
        Cell: () => <FontAwesomeIcon icon={faArrowRight} />,
      },
      {
        Header: (
          <HeaderCell>
            <FormattedMessage id="form.field.name" />
          </HeaderCell>
        ),
        accessor: "cleanedName",
        Cell: ({ row }: CellProps<SyncSchemaField>) => row.original.cleanedName,
      },
      {
        Header: (
          <HeaderCell>
            <FormattedMessage id="form.field.dataType" />
          </HeaderCell>
        ),
        accessor: "format",
        Cell: ({ row }: CellProps<SyncSchemaField>) => useTranslateDataType(row.original),
      },
      /*
      { Destination - dataType column
        In the design, but we may be unable to get the destination data type
        <HeaderCell lighter>
          <FormattedMessage id="form.field.dataType" />
        </HeaderCell>
      },
    */
    ],
    [isCursor, isPrimaryKey, onCursorSelect, onPkSelect, shouldDefineCursor, shouldDefinePk]
  );

  return <Table columns={columns} data={syncSchemaFields} light />;
};

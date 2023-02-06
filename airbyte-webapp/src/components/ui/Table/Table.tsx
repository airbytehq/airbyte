import classNames from "classnames";
import React, { memo, useMemo } from "react";
import { Cell, Column, ColumnInstance, SortingRule, useSortBy, useTable } from "react-table";

import styles from "./Table.module.scss";

interface HeaderProps extends ColumnInstance<Record<string, unknown>> {
  headerHighlighted?: boolean;
  collapse?: boolean;
  customWidth?: number;
  responsive?: boolean;
}

interface CellProps extends Cell {
  column: HeaderProps;
}

interface TableProps {
  light?: boolean;
  columns: Array<HeaderProps | Column<Record<string, unknown>>>;
  erroredRows?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onClickRow?: (data: any) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  sortBy?: Array<SortingRule<any>>;
  testId?: string;
}

export const Table: React.FC<TableProps> = memo(({ columns, data, onClickRow, erroredRows, sortBy, light, testId }) => {
  const [plugins, config] = useMemo(() => {
    const pl = [];
    const plConfig: Record<string, unknown> = {};

    if (sortBy) {
      pl.push(useSortBy);
      plConfig.initialState = { sortBy };
    }
    return [pl, plConfig];
  }, [sortBy]);
  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable(
    {
      ...config,
      columns,
      data,
    },
    ...plugins
  );

  return (
    <table
      className={classNames(styles.tableView, { [styles.light]: light })}
      {...getTableProps()}
      data-testid={testId}
    >
      <thead>
        {headerGroups.map((headerGroup, key) => (
          <tr {...headerGroup.getHeaderGroupProps()} key={`table-header-${key}`}>
            {headerGroup.headers.map((column: HeaderProps, columnKey) => (
              <th
                className={classNames(styles.tableHeader, {
                  [styles.light]: light,
                  [styles.highlighted]: column.headerHighlighted,
                })}
                {...column.getHeaderProps()}
                style={{
                  width: column.customWidth ? `${column.customWidth}%` : column.collapse ? "0.0000000001%" : "auto",
                }}
                key={`table-column-${key}-${columnKey}`}
              >
                {column.render("Header")}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <tr
              className={classNames(styles.tableRow, {
                [styles.hasClick]: !!onClickRow,
                [styles.erroredRows]: erroredRows && !!row.original.error,
              })}
              {...row.getRowProps()}
              onClick={() => onClickRow?.(row.original)}
              key={`table-row-${row.id}`}
            >
              {row.cells.map((cell: CellProps, key) => {
                return (
                  <td
                    className={classNames(styles.tableData, { [styles.responsive]: cell.column.responsive })}
                    {...cell.getCellProps()}
                    style={{
                      width: cell.column.customWidth
                        ? `${cell.column.customWidth}%`
                        : cell.column.collapse
                        ? "0.0000000001%"
                        : "auto",
                    }}
                    key={`table-cell-${row.id}-${key}`}
                  >
                    {cell.render("Cell")}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
});

import { ColumnDef, flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import classNames from "classnames";
import { PropsWithChildren } from "react";

import styles from "./NextTable.module.scss";

export interface TableProps<T> {
  className?: string;
  // We can leave type any here since useReactTable options.columns itself is waiting for Array<ColumnDef<T, any>>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: Array<ColumnDef<T, any>>;
  data: T[];
  light?: boolean;
  onClickRow?: (data: T) => void;
  testId?: string;
}

export const NextTable = <T,>({
  testId,
  className,
  columns,
  data,
  light,
  onClickRow,
}: PropsWithChildren<TableProps<T>>) => {
  const table = useReactTable({
    columns,
    data,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table className={classNames(styles.table, className, { [styles.light]: light })} data-testid={testId}>
      <thead className={styles.thead}>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={`table-header-${headerGroup.id}}`}>
            {headerGroup.headers.map((header) => {
              const { meta } = header.column.columnDef;
              return (
                <th
                  colSpan={header.colSpan}
                  className={classNames(
                    styles.th,
                    {
                      [styles.light]: light,
                    },
                    meta?.thClassName
                  )}
                  key={`table-column-${headerGroup.id}-${header.id}`}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              );
            })}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => {
          return (
            <tr
              className={classNames(styles.tr, { [styles.clickable]: !!onClickRow })}
              key={`table-row-${row.id}`}
              onClick={() => onClickRow?.(row.original)}
            >
              {row.getVisibleCells().map((cell) => (
                <td
                  className={classNames(styles.td, cell.column.columnDef.meta?.tdClassName, {
                    [styles.responsive]: cell.column.columnDef.meta?.responsive,
                  })}
                  key={`table-cell-${row.id}-${cell.id}`}
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

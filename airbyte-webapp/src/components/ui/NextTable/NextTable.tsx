import { ColumnDef, flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import classNames from "classnames";
import { PropsWithChildren } from "react";

import { ConnectionScheduleData } from "core/request/AirbyteClient";

import styles from "./NextTable.module.scss";

type TData<T> = T & {
  error?: unknown;
};

export interface TableProps<T> {
  className?: string;
  columns: Array<
    | ColumnDef<TData<T>, string>
    | ColumnDef<TData<T>, number>
    | ColumnDef<TData<T>, boolean>
    | ColumnDef<TData<T>, ConnectionScheduleData>
  >;
  data: Array<TData<T>>;
  erroredRows?: boolean;
  light?: boolean;
  onClickRow?: (data: TData<T>) => void;
}

export const NextTable = <T,>({
  columns,
  data,
  onClickRow,
  className,
  erroredRows,
  light,
}: PropsWithChildren<TableProps<TData<T>>>) => {
  const table = useReactTable({
    columns,
    data,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table className={classNames(styles.table, className, { [styles.light]: light })}>
      <thead className={styles.thead}>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={`table-header-${headerGroup.id}}`}>
            {headerGroup.headers.map((header) => {
              const { meta } = header.column.columnDef;
              return (
                <th
                  colSpan={header.colSpan}
                  className={classNames(styles.th, meta?.thClassName, {
                    [styles.highlighted]: meta?.headerHighlighted,
                    [styles.light]: light,
                    [styles.collapse]: meta?.collapse,
                  })}
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
        {table.getRowModel().rows.map((row) => (
          <tr
            className={classNames(styles.tr, {
              [styles.withError]: erroredRows && !!row.original.error,
              [styles.clickable]: !!onClickRow,
            })}
            key={`table-row-${row.id}`}
            onClick={() => onClickRow?.(row.original)}
          >
            {row.getVisibleCells().map((cell) => (
              <td
                className={classNames(styles.td, cell.column.columnDef.meta?.tdClassName)}
                key={`table-cell-${row.id}-${cell.id}`}
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

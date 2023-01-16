import { ColumnDef, flexRender, useReactTable, getCoreRowModel, ColumnSort } from "@tanstack/react-table";
import classNames from "classnames";
import { PropsWithChildren } from "react";

import styles from "./NextTable.module.scss";

type TData<T> = T & {
  error?: unknown;
};

export interface TableProps<T> {
  className?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: Array<ColumnDef<TData<T>, any>>;
  data: Array<TData<T>>;
  erroredRows?: boolean;
  light?: boolean;
  onClickRow?: (data: TData<T>) => void;
  columnSort?: ColumnSort[];
}

export const NextTable = <T,>({
  className,
  columns,
  data,
  erroredRows,
  light,
  onClickRow,
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

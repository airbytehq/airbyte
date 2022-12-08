import { ColumnDef, flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import classNames from "classnames";
import { PropsWithChildren } from "react";

import styles from "./NextTable.module.scss";

export interface TableProps<TData> {
  data: TData[];
  columns: Array<ColumnDef<TData>>;
  onClickRow?: (data: unknown) => void;
  className?: string;
}

export const NextTable = <TData,>({ columns, data, onClickRow, className }: PropsWithChildren<TableProps<TData>>) => {
  const table = useReactTable({
    columns,
    data,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table className={classNames(styles.table, className)}>
      <thead className={styles.thead}>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={`table-header-${headerGroup.id}}`}>
            {headerGroup.headers.map((header) => (
              <th
                colSpan={header.colSpan}
                className={classNames(styles.th, header.column.columnDef.meta?.thClassName)}
                key={`table-column-${headerGroup.id}-${header.id}`}
              >
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr className={styles.tr} key={`table-row-${row.id}`} onClick={() => onClickRow?.(row.original)}>
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

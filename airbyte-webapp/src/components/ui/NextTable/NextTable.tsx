import { ColumnDef, flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import { ColumnMeta } from "@tanstack/table-core";
import classNames from "classnames";
import { CSSProperties, PropsWithChildren } from "react";

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

const getStyleFromColumnMeta = <T,>(meta: ColumnMeta<T, unknown>): CSSProperties => {
  const style: CSSProperties = {};
  if (meta?.customWidth) {
    style.width = `${meta.customWidth}%`;
  }
  if (meta?.customPadding?.left) {
    style.paddingLeft = `${meta.customPadding.left}px`;
  }
  if (meta?.customPadding?.right) {
    style.paddingRight = `${meta.customPadding.right}px`;
  }
  return style;
};

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
              const style = getStyleFromColumnMeta<TData<T>>(meta as ColumnMeta<T, unknown>);
              return (
                <th
                  colSpan={header.colSpan}
                  className={classNames(styles.th, meta?.thClassName, {
                    [styles.highlighted]: meta?.headerHighlighted,
                    [styles.light]: light,
                    [styles.collapse]: meta?.collapse,
                  })}
                  key={`table-column-${headerGroup.id}-${header.id}`}
                  style={style}
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

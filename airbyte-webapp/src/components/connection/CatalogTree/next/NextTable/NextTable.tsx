import classNames from "classnames";
import React, { memo, useMemo } from "react";
import { Column, SortingRule, useSortBy, useTable } from "react-table";
import styled from "styled-components";

import { Card } from "../../../../ui/Card";
import styles from "./NextTable.module.scss";

const TableView = styled(Card).attrs({ as: "table" })<{ light?: boolean }>`
  border-spacing: 0;
  width: 100%;
  max-width: 100%;
  border-radius: 10px;
  box-shadow: ${({ light, theme }) => (light ? "none" : `0 2px 4px ${theme.cardShadowColor}`)};
};
`;

interface TableProps {
  light?: boolean;
  columns: ReadonlyArray<Column<Record<string, unknown>>>;
  erroredRows?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onClickRow?: (data: any) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  sortBy?: Array<SortingRule<any>>;
}

export const NextTable: React.FC<TableProps> = memo(({ columns, data, onClickRow, sortBy, light }) => {
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
    <TableView {...getTableProps()} light={light}>
      <thead>
        {headerGroups.map((headerGroup, key) => (
          <tr {...headerGroup.getHeaderGroupProps()} key={`table-header-${key}`}>
            {headerGroup.headers.map((column, columnKey) => (
              <th
                {...column.getHeaderProps([
                  {
                    className: classNames(
                      styles.th,
                      // @ts-expect-error will be fixed when with typings
                      column.thClassName
                    ),
                  },
                ])}
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
              {...row.getRowProps()}
              className={styles.tr}
              key={`table-row-${row.id}`}
              onClick={() => onClickRow?.(row.original)}
            >
              {row.cells.map((cell, key) => {
                return (
                  <td
                    {...cell.getCellProps([
                      {
                        className: classNames(
                          styles.td,
                          // @ts-expect-error will be fixed when with typings
                          cell.column.tdClassName
                        ),
                      },
                    ])}
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
    </TableView>
  );
});

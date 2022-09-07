import React, { memo, useMemo } from "react";
import { Cell, Column, ColumnInstance, SortingRule, useSortBy, useTable } from "react-table";
import styled from "styled-components";

import { Card } from "components";

interface PaddingProps {
  left?: number;
  right?: number;
}

type IHeaderProps = {
  headerHighlighted?: boolean;
  collapse?: boolean;
  customWidth?: number;
  customPadding?: PaddingProps;
} & ColumnInstance;

type ICellProps = {
  column: IHeaderProps;
} & Cell;

type IThProps = {
  highlighted?: boolean;
  collapse?: boolean;
  customWidth?: number;
  customPadding?: PaddingProps;
  light?: boolean;
} & React.ThHTMLAttributes<HTMLTableHeaderCellElement>;

const TableView = styled(Card).attrs({ as: "table" })<{ light?: boolean }>`
  border-spacing: 0;
  width: 100%;
  max-width: 100%;
  border-radius: 10px;
  box-shadow: ${({ light, theme }) => (light ? "none" : `0 2px 4px ${theme.cardShadowColor}`)};
};
`;

const Tr = styled.tr<{
  hasClick?: boolean;
  erroredRows?: boolean;
}>`
  background: ${({ theme, erroredRows }) => (erroredRows ? theme.dangerTransparentColor : theme.whiteColor)};
  cursor: ${({ hasClick }) => (hasClick ? "pointer" : "auto")};
`;

const Td = styled.td<{
  collapse?: boolean;
  customWidth?: number;
  customPadding?: PaddingProps;
}>`
  padding: ${({ customPadding }) => `16px ${customPadding?.right ?? 13}px 16px ${customPadding?.left ?? 13}px`};
  font-size: 12px;
  line-height: 15px;
  font-weight: normal;
  color: ${({ theme }) => theme.darkPrimaryColor};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  width: ${({ collapse, customWidth }) => (customWidth ? `${customWidth}%` : collapse ? "0.0000000001%" : "auto")};

  tr:last-child > & {
    border-bottom: none;

    &:first-child {
      border-radius: 0 0 0 10px;
    }

    &:last-child {
      border-radius: 0 0 10px 0;
    }
  }
`;

const Th = styled.th<IThProps>`
  background: ${({ theme, light }) => (light ? "none" : theme.textColor)};
  padding: ${({ customPadding }) => `9px ${customPadding?.right ?? 13}px 10px ${customPadding?.left ?? 13}px`};
  text-align: left;
  font-size: ${({ light }) => (light ? 11 : 10)}px;
  line-height: 12px;
  color: ${({ theme, highlighted }) => (highlighted ? theme.whiteColor : theme.lightTextColor)};
  border-bottom: ${({ theme, light }) => (light ? "none" : ` 1px solid ${theme.backgroundColor}`)};
  width: ${({ collapse, customWidth }) => (customWidth ? `${customWidth}%` : collapse ? "0.0000000001%" : "auto")};
  font-weight: ${({ light }) => (light ? 400 : 600)};
  text-transform: ${({ light }) => (light ? "capitalize" : "uppercase")};

  &:first-child {
    padding-left: ${({ light }) => (light ? 13 : 45)}px;
    border-radius: 10px 0 0;
  }

  &:last-child {
    padding-left: 45px;
    border-radius: 0 10px 0 0;
  }
`;

interface IProps {
  light?: boolean;
  columns: Array<IHeaderProps | Column<Record<string, unknown>>>;
  erroredRows?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onClickRow?: (data: any) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  sortBy?: Array<SortingRule<any>>;
}

const Table: React.FC<IProps> = ({ columns, data, onClickRow, erroredRows, sortBy, light }) => {
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
            {headerGroup.headers.map((column: IHeaderProps, columnKey) => (
              <Th
                {...column.getHeaderProps()}
                highlighted={column.headerHighlighted}
                collapse={column.collapse}
                customPadding={column.customPadding}
                customWidth={column.customWidth}
                key={`table-column-${key}-${columnKey}`}
                light={light}
              >
                {column.render("Header")}
              </Th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <Tr
              {...row.getRowProps()}
              key={`table-row-${row.id}`}
              hasClick={!!onClickRow}
              onClick={() => onClickRow?.(row.original)}
              erroredRows={erroredRows && !!row.original.error}
            >
              {row.cells.map((cell: ICellProps, key) => {
                return (
                  <Td
                    {...cell.getCellProps()}
                    collapse={cell.column.collapse}
                    customPadding={cell.column.customPadding}
                    customWidth={cell.column.customWidth}
                    key={`table-cell-${row.id}-${key}`}
                  >
                    {cell.render("Cell")}
                  </Td>
                );
              })}
            </Tr>
          );
        })}
      </tbody>
    </TableView>
  );
};

export default memo(Table);

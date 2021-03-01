import React, { memo } from "react";
import styled from "styled-components";
import { ColumnInstance, useTable, Column, Cell } from "react-table";

type IHeaderProps = {
  headerHighlighted?: boolean;
  collapse?: boolean;
  customWidth?: number;
} & ColumnInstance;

type ICellProps = {
  column: IHeaderProps;
} & Cell;

type IThProps = {
  highlighted?: boolean;
  collapse?: boolean;
  customWidth?: number;
} & React.ThHTMLAttributes<HTMLTableHeaderCellElement>;

const TableView = styled.table`
  border-spacing: 0;
  width: 100%;
  overflow: hidden;
  background: ${({ theme }) => theme.whiteColor};
  border: 1px solid ${({ theme }) => theme.greyColor20};
  box-shadow: 0 1px 2px 0 ${({ theme }) => theme.shadowColor};
  border-radius: 8px;
  max-width: 100%;
`;

const Tr = styled.tr<{
  hasClick?: boolean;
  erroredRows?: boolean;
}>`
  background: ${({ theme, erroredRows }) =>
    erroredRows ? theme.dangerTransparentColor : theme.whiteColor};
  cursor: ${({ hasClick }) => (hasClick ? "pointer" : "auto")};
`;

const Td = styled.td<{ collapse?: boolean; customWidth?: number }>`
  padding: 16px 13px;
  font-size: 14px;
  line-height: 17px;
  font-weight: normal;
  color: ${({ theme }) => theme.darkPrimaryColor};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  width: ${({ collapse, customWidth }) =>
    customWidth ? `${customWidth}%` : collapse ? "0.0000000001%" : "auto"};

  tr:last-child > & {
    border-bottom: none;
  }
`;

const Th = styled.th<IThProps>`
  background: ${({ theme }) => theme.greyColor0};
  padding: 7px 13px 8px;
  text-align: left;
  font-size: 14px;
  line-height: 17px;
  font-weight: normal;
  opacity: ${({ highlighted }) => (highlighted ? 1 : 0.6)};
  color: ${({ theme }) => theme.darkPrimaryColor};
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  width: ${({ collapse, customWidth }) =>
    customWidth ? `${customWidth}%` : collapse ? "0.0000000001%" : "auto"};

  &:first-child {
    padding-left: 45px;
  }
`;

type IProps = {
  columns: Array<IHeaderProps | Column<Record<string, unknown>>>;
  erroredRows?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onClickRow?: (data: any) => void;
};

const Table: React.FC<IProps> = ({
  columns,
  data,
  onClickRow,
  erroredRows,
}) => {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({
    columns,
    data,
  });

  return (
    <TableView {...getTableProps()}>
      <thead>
        {headerGroups.map((headerGroup, key) => (
          <tr
            {...headerGroup.getHeaderGroupProps()}
            key={`table-header-${key}`}
          >
            {headerGroup.headers.map((column: IHeaderProps, columnKey) => (
              <Th
                {...column.getHeaderProps()}
                highlighted={column.headerHighlighted}
                collapse={column.collapse}
                customWidth={column.customWidth}
                key={`table-column-${key}-${columnKey}`}
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
            <>
              <Tr
                {...row.getRowProps()}
                key={`table-row-${row.id}`}
                hasClick={!!onClickRow}
                onClick={() => onClickRow?.(row.original)}
                erroredRows={erroredRows && !!row.original.error}
              >
                {
                  // @ts-ignore needs to address proper types for table
                  row.cells.map((cell: ICellProps, key) => {
                    return (
                      <Td
                        {...cell.getCellProps()}
                        collapse={cell.column.collapse}
                        customWidth={cell.column.customWidth}
                        key={`table-cell-${row.id}-${key}`}
                      >
                        {cell.render("Cell")}
                      </Td>
                    );
                  })
                }
              </Tr>
            </>
          );
        })}
      </tbody>
    </TableView>
  );
};

export default memo(Table);

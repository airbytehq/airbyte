import React, { memo } from "react";
import styled from "styled-components";
import { ColumnInstance, useTable, Column } from "react-table";

type IHeaderProps = {
  headerHighlighted?: boolean;
} & ColumnInstance;

type IProps = {
  columns: Array<IHeaderProps | Column>;
  data: Array<object>;
  onClickRow?: (data: object) => void;
};

type IThProps = {
  highlighted?: boolean;
} & React.ThHTMLAttributes<HTMLTableHeaderCellElement>;

const TableView = styled.table`
  border: none;
  border-spacing: 0;
  width: 100%;
`;

const Tr = styled.tr<{ hasClick?: boolean }>`
  background: ${({ theme }) => theme.whiteColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  margin-bottom: 5px;
  border-radius: 8px;
  cursor: ${({ hasClick }) => (hasClick ? "pointer" : "auto")};

  &:hover {
    box-shadow: 0 1px 2px
      ${({ theme, hasClick }) =>
        hasClick ? theme.primaryColor25 : theme.shadowColor};
  }
`;

const Td = styled.td`
  padding: 21px 17px;
  font-size: 14px;
  line-height: 19px;
  font-weight: 500;
  color: ${({ theme }) => theme.darkPrimaryColor};

  &:first-child {
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
  }

  &:last-child {
    border-bottom-right-radius: 8px;
    border-top-right-radius: 8px;
  }
`;

const Th = styled.th<IThProps>`
  padding: 0 17px 11px;
  text-align: left;
  font-size: 14px;
  line-height: 17px;
  font-weight: ${props => (props.highlighted ? "500" : "normal")};
  color: ${({ theme, highlighted }) =>
    highlighted ? theme.darkPrimaryColor : theme.darkPrimaryColor60};
`;

const Space = styled.tr`
  height: 5px;
`;

const Table: React.FC<IProps> = ({ columns, data, onClickRow }) => {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow
  } = useTable({
    columns,
    data
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
                key={`table-column-${key}-${columnKey}`}
              >
                {column.render("Header")}
              </Th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map(row => {
          prepareRow(row);
          return (
            <>
              <Tr
                {...row.getRowProps()}
                key={`table-row-${row.id}`}
                hasClick={!!onClickRow}
                onClick={() => onClickRow && onClickRow(row.original)}
              >
                {row.cells.map((cell, key) => {
                  return (
                    <Td
                      {...cell.getCellProps()}
                      key={`table-cell-${row.id}-${key}`}
                    >
                      {cell.render("Cell")}
                    </Td>
                  );
                })}
              </Tr>
              <Space key={`table-space-${row.id}`} />
            </>
          );
        })}
      </tbody>
    </TableView>
  );
};

export default memo(Table);

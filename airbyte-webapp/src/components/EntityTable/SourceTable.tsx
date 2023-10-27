import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import Table from "components/Table";

import useRouter from "hooks/useRouter";

import ConnectionCopyCell from "./components/ConnectionCopyCell";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import NewTabIconButton from "./components/NewTabIconButton";
import SortButton from "./components/SortButton";
import styles from "./ImplementationTable.module.scss";
import { SortOrderEnum, SourceTableDataItem } from "./types";
import { RoutePaths } from "../../pages/routePaths";

interface IProps {
  data: SourceTableDataItem[];
  entity: "source";
  onClickRow?: (data: SourceTableDataItem) => void;
}

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

const SourceTable: React.FC<IProps> = ({ data, entity }) => {
  const { query, push } = useRouter();
  const sortBy = query.sortBy || "entity";
  const sortOrder = query.order || SortOrderEnum.ASC;

  const onSortClick = useCallback(
    (field: string) => {
      const order =
        sortBy !== field ? SortOrderEnum.ASC : sortOrder === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;
      push({
        search: queryString.stringify(
          {
            sortBy: field,
            order,
          },
          { skipNull: true }
        ),
      });
    },
    [push, sortBy, sortOrder]
  );

  // const sortData = useCallback(
  //   (a, b) => {
  //     let result;
  //     if (sortBy === "lastSync") {
  //       result = b[sortBy] - a[sortBy];
  //     } else {
  //       result = a[`${sortBy}Name`].toLowerCase().localeCompare(b[`${sortBy}Name`].toLowerCase());
  //     }

  //     if (sortOrder === SortOrderEnum.DESC) {
  //       return -1 * result;
  //     }

  //     return result;
  //   },
  //   [sortBy, sortOrder]
  // );

  const routerPath = entity === "source" ? RoutePaths.Source : RoutePaths.Destination;
  const clickEditRow = (sourceId: string) => push(`/${routerPath}/${sourceId}`);

  // const sortingData = React.useMemo(() => data.sort(sortData), [sortData, data]);

  const clickCopyRow = (sourceId: string) => {
    push(`${sourceId}/copy`, {});
  };

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.name" />
            <SortButton
              wasActive={sortBy === "entity"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("entity")}
            />
          </div>
        ),
        headerHighlighted: true,
        accessor: "name",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<SourceTableDataItem>) => (
          <NameColums>
            <NameCell value={cell.value} onClickRow={() => clickEditRow(row.original.sourceId)} />
            <NewTabIconButton id={row.original.sourceId} type="Source" />
          </NameColums>
        ),
      },
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.connector" />
            <SortButton
              wasActive={sortBy === "connector"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("connector")}
            />
          </div>
        ),
        customWidth: 40,
        accessor: "sourceName",
        Cell: ({ cell }: CellProps<SourceTableDataItem>) => <ConnectorCell value={cell.value} />,
      },

      {
        Header: <FormattedMessage id="sources.editText" />,
        id: "edit",
        accessor: "sourceId",
        Cell: ({ cell }: CellProps<SourceTableDataItem>) => (
          <ConnectionSettingsCell id={cell.value} onClick={() => clickEditRow(cell.value)} />
        ),
      },
      {
        Header: <FormattedMessage id="sources.copyText" />,
        id: "copy",
        accessor: "sourceId",
        Cell: ({ cell }: CellProps<SourceTableDataItem>) => (
          <ConnectionCopyCell
            onClick={() => {
              clickCopyRow(cell.value);
            }}
          />
        ),
      },
    ],
    [entity, onSortClick, sortBy, sortOrder]
  );

  return (
    <div className={styles.content}>
      <Table columns={columns} data={data} erroredRows />
    </div>
  );
};

export default SourceTable;

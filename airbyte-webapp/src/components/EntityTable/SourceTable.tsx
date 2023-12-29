import { IconButton } from "@mui/material";
import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import { SortDownIcon } from "components/icons/SortDownIcon";
import { SortUpIcon } from "components/icons/SortUpIcon";
import Table from "components/Table";

import useRouter from "hooks/useRouter";

import ConnectionCopyCell from "./components/ConnectionCopyCell";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import NewTabIconButton from "./components/NewTabIconButton";
import styles from "./ImplementationTable.module.scss";
import { SortOrderEnum, SourceTableDataItem } from "./types";
import { RoutePaths } from "../../pages/routePaths";

interface IProps {
  data: SourceTableDataItem[];
  entity: "source";
  onClickRow?: (data: SourceTableDataItem) => void;
  setSortFieldName?: any;
  setSortDirection?: any;
  onSelectFilter?: any;
}

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

const SourceTable: React.FC<IProps> = ({ data, entity, setSortFieldName, setSortDirection, onSelectFilter }) => {
  const { push } = useRouter();

  useEffect(() => {
    // Set initial sort order to DESC when the component mounts
    setSortFieldName("name");
    onSelectFilter("sortFieldName", "name");
    setSortDirection(SortOrderEnum.DESC);
    setLocalSortOrder(SortOrderEnum.DESC);
  }, []);

  const [localSortOrder, setLocalSortOrder] = useState(SortOrderEnum.DESC);
  const [sourceSortOrder, setSourceSortOrder] = useState(SortOrderEnum.DESC);

  const routerPath = entity === "source" ? RoutePaths.Source : RoutePaths.Destination;
  const clickEditRow = (sourceId: string) => push(`/${routerPath}/${sourceId}`);

  const clickCopyRow = (sourceId: string) => {
    push(`${sourceId}/copy`, {});
  };

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.name" />
            <IconButton
              onClick={() => {
                setSortFieldName("name");
                onSelectFilter("sortFieldName", "name");

                setSortDirection((prevSortOrder: any) => {
                  const newSortOrder = prevSortOrder === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;

                  onSelectFilter("sortDirection", newSortOrder);
                  setLocalSortOrder(newSortOrder);
                  return newSortOrder;
                });
              }}
              sx={{ paddingTop: "1px" }}
            >
              {localSortOrder === SortOrderEnum.ASC ? <SortDownIcon /> : <SortUpIcon />}
            </IconButton>
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

            <IconButton
              onClick={() => {
                setSortFieldName("sourceName");
                setSourceSortOrder((prev) => {
                  const newSortOrder = prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;
                  onSelectFilter("sortFieldName", "sourceName");
                  onSelectFilter("sortDirection", newSortOrder);
                  return newSortOrder;
                });
              }}
              sx={{ paddingTop: "1px" }}
            >
              {sourceSortOrder === SortOrderEnum.ASC ? <SortDownIcon /> : <SortUpIcon />}
            </IconButton>
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
    [entity, localSortOrder, sourceSortOrder]
  );

  return (
    <div className={styles.content}>
      <Table columns={columns} data={data} erroredRows />
    </div>
  );
};

export default SourceTable;

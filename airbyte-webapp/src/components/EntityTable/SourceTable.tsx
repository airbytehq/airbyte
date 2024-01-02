import { IconButton } from "@mui/material";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import { SortDescIcon } from "components/icons/SortDescIcon";
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
  localSortOrder?: any;
  setLocalSortOrder?: any;
  sourceSortOrder?: any;
  setSourceSortOrder?: any;
}

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

const SourceTable: React.FC<IProps> = ({
  data,
  entity,
  setSortFieldName,
  setSortDirection,
  onSelectFilter,
  localSortOrder,
  setLocalSortOrder,
  sourceSortOrder,
  setSourceSortOrder,
}) => {
  const { push } = useRouter();

  const routerPath = entity === "source" ? RoutePaths.Source : RoutePaths.Destination;
  const clickEditRow = (sourceId: string) => push(`/${routerPath}/${sourceId}`);

  const clickCopyRow = (sourceId: string) => {
    push(`${sourceId}/copy`, {});
  };

  const columns = useMemo(
    () => [
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.name" />
            <IconButton
              onClick={() => {
                setSortFieldName("name");
                setLocalSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  // const newSortOrder = prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;
                  setSortDirection(newSortOrder);
                  onSelectFilter("sortFieldName", "name");
                  onSelectFilter("sortDirection", newSortOrder);
                  return newSortOrder;
                });
              }}
              sx={{ paddingTop: "1px" }}
            >
              {localSortOrder === "" ? (
                <SortUpIcon />
              ) : localSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
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
                setSourceSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  onSelectFilter("sortFieldName", "sourceName");
                  onSelectFilter("sortDirection", newSortOrder);
                  return newSortOrder;
                });
              }}
              sx={{ paddingTop: "1px" }}
            >
              {sourceSortOrder === "" ? (
                <SortUpIcon />
              ) : sourceSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
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

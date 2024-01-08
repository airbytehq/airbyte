import { IconButton } from "@mui/material";
import queryString from "query-string";
import { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import { SortDescIcon } from "components/icons/SortDescIcon";
import { SortDownIcon } from "components/icons/SortDownIcon";
import { SortUpIcon } from "components/icons/SortUpIcon";
import Table from "components/Table";

import { DestinationRead } from "core/request/AirbyteClient";
import useRouter from "hooks/useRouter";

import ConnectionCopyCell from "./components/ConnectionCopyCell";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import NameCell from "./components/NameCell";
import NewTabIconButton from "./components/NewTabIconButton";
import styles from "./ImplementationTable.module.scss";
import { SortOrderEnum } from "./types";
import { RoutePaths } from "../../pages/routePaths";

interface IProps {
  data: DestinationRead[];
  entity: "destination";
  onClickRow?: (data: DestinationRead) => void;
  setSortFieldName?: any;
  setSortDirection?: any;
  onSelectFilter?: any;
  localSortOrder?: any;
  setLocalSortOrder?: any;
  destinationSortOrder?: any;
  setDestinationSortOrder?: any;
  query?: any;
  push?: any;
  pageCurrent?: any;
  pageSize?: any;
}

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

const DestinationTable: React.FC<IProps> = ({
  data,
  entity,
  setSortDirection,
  setSortFieldName,
  onSelectFilter,
  localSortOrder,
  setLocalSortOrder,
  destinationSortOrder,
  setDestinationSortOrder,
  pageCurrent,
  pageSize,
}) => {
  const { query, push } = useRouter();
  const sortBy = query.sortBy;
  const sortOrder = query.order;
  const routerPath = entity === "destination" ? RoutePaths.Destination : RoutePaths.Destination;
  const clickEditRow = (destinationId: string) => push(`/${routerPath}/${destinationId}`);

  const clickCopyRow = (destinationId: string) => {
    push(`${destinationId}/copy`, {});
  };
  const onSortClick = useCallback(
    (field: string) => {
      let newSortOrder: SortOrderEnum | "" = "";

      if (sortBy !== field) {
        // Clicking on a new column
        newSortOrder = SortOrderEnum.ASC;
      } else {
        // Clicking on the same column
        newSortOrder =
          sortOrder === SortOrderEnum.ASC
            ? SortOrderEnum.DESC
            : sortOrder === SortOrderEnum.DESC
            ? ""
            : SortOrderEnum.ASC;
      }
      /*
       const newSearchParams: { sortBy?: string; order?: string,pageCurrent?:string|number} = {};
      console.log(newSearchParams,'sortfunc')
      if (newSortOrder !== "") {
        newSearchParams.sortBy = field;
        newSearchParams.order = newSortOrder;
        newSearchParams.pageCurrent=pageCurrent
      } else {
        newSearchParams.sortBy = "";
        newSearchParams.order = "";
        newSearchParams.pageCurrent=pageCurrent
      }
     */

      const newSearchParams: { sortBy?: string; order?: string; pageSize?: any; pageCurrent?: any } = {};
      if (newSortOrder !== "") {
        newSearchParams.sortBy = field;
        newSearchParams.order = newSortOrder;
        newSearchParams.pageCurrent = pageCurrent;
        newSearchParams.pageSize = pageSize;
      } else {
        newSearchParams.sortBy = "";
        newSearchParams.order = "";
        newSearchParams.pageCurrent = pageCurrent;
        newSearchParams.pageSize = pageSize;
      }

      push({
        search: queryString.stringify(newSearchParams, { skipNull: true }),
      });
    },
    [push, sortBy, sortOrder, query]
  );

  const columns = useMemo(
    () => [
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.name" />
            <IconButton
              onClick={() => {
                setSortFieldName("name");
                onSortClick("name");
                setLocalSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  setSortDirection(newSortOrder);
                  setDestinationSortOrder("");
                  onSelectFilter("sortFieldName", "name", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
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
        Cell: ({ cell, row }: CellProps<DestinationRead>) => (
          <NameColums>
            <NameCell value={cell.value} onClickRow={() => clickEditRow(row.original.destinationId)} />
            <NewTabIconButton id={row.original.destinationId} type="Destination" />
          </NameColums>
        ),
      },
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.connector" />
            <IconButton
              onClick={() => {
                setSortFieldName("destinationName");
                onSortClick("destinationName");
                setDestinationSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  setLocalSortOrder("");
                  onSelectFilter("sortFieldName", "destinationName", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
                  return newSortOrder;
                });
              }}
              sx={{ paddingTop: "1px" }}
            >
              {destinationSortOrder === "" ? (
                <SortUpIcon />
              ) : destinationSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
            </IconButton>
          </div>
        ),
        customWidth: 40,
        accessor: "destinationName",
        Cell: ({ cell }: CellProps<DestinationRead>) => <ConnectorCell value={cell.value} />,
      },

      {
        Header: <FormattedMessage id="sources.editText" />,
        id: "edit",
        accessor: "destinationId",
        Cell: ({ cell }: CellProps<DestinationRead>) => (
          <ConnectionSettingsCell id={cell.value} onClick={() => clickEditRow(cell.value)} />
        ),
      },
      {
        Header: <FormattedMessage id="sources.copyText" />,
        id: "copy",
        accessor: "destinationId",
        Cell: ({ cell }: CellProps<DestinationRead>) => (
          <ConnectionCopyCell
            onClick={() => {
              clickCopyRow(cell.value);
            }}
          />
        ),
      },
    ],
    [entity, localSortOrder, destinationSortOrder]
  );

  return (
    <div className={styles.content}>
      <Table columns={columns} data={data} erroredRows />
    </div>
  );
};

export default DestinationTable;

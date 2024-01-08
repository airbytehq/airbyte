import { Box, IconButton, Tooltip } from "@mui/material";
import queryString from "query-string";
import { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import { DisabledIcon } from "components/icons/DisabledIcon";
import { FailedIcon } from "components/icons/FailedIcon";
import { GreenIcon } from "components/icons/GreenIcon";
import { GreenLoaderIcon } from "components/icons/GreenLoaderIcon";
import { NotStartedIcon } from "components/icons/NotStartedIcon";
import { SortDescIcon } from "components/icons/SortDescIcon";
import { SortDownIcon } from "components/icons/SortDownIcon";
import { SortUpIcon } from "components/icons/SortUpIcon";
import { WaitingIcon } from "components/icons/WaitingIcon";
import { LabeledSwitch } from "components/LabeledSwitch";
import Table from "components/Table";

import { FeatureItem, useFeature } from "hooks/services/Feature";
import useRouter from "hooks/useRouter";

import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import NewTabIconButton from "./components/NewTabIconButton";
import { ITableDataItem, SortOrderEnum } from "./types";
import { RoutePaths } from "../../pages/routePaths";

const SwitchContent = styled.div`
  display: flex;
  align-items: center;
`;

const HeaderColumns = styled.div`
  display: flex;
  flex-wrap: nowrap;
  min-width: 100px;
`;

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

interface IProps {
  data: ITableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ITableDataItem) => void;
  onChangeStatus?: (id: string, status: string | undefined) => void;
  onSync?: (id: string) => void;
  rowId?: string;
  statusLoading?: boolean;
  switchSize?: string;
  setSortFieldName?: any;
  setSortDirection?: any;
  onSelectFilter?: any;
  localSortOrder?: any;
  setLocalSortOrder?: any;
  connectorSortOrder?: any;
  setConnectorSortOrder?: any;
  entitySortOrder?: any;
  setEntitySortOrder?: any;
  statusSortOrder?: any;
  setStatusSortOrder?: any;
  pageCurrent?: any;
  pageSize?: any;
}
//
const ConnectionTable: React.FC<IProps> = ({
  data,
  entity,
  onChangeStatus,
  onSync,
  rowId,
  statusLoading,
  setSortDirection,
  setSortFieldName,
  onSelectFilter,
  localSortOrder,
  setLocalSortOrder,
  connectorSortOrder,
  setConnectorSortOrder,
  entitySortOrder,
  setEntitySortOrder,
  statusSortOrder,
  setStatusSortOrder,
  pageCurrent,
  pageSize,
}) => {
  const { query, push } = useRouter();
  const sortBy = query.sortBy;
  const sortOrder = query.order;
  const allowSync = useFeature(FeatureItem.AllowSync);
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

      const newSearchParams: { sortBy?: string; order?: string; pageCurrent?: any; pageSize?: any } = {};
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
  const onClickRows = (connectionId: string) => push(`/${RoutePaths.Connections}/${connectionId}`);

  const columns = useMemo(
    () => [
      onChangeStatus
        ? {
            Header: "",
            accessor: "lastSyncStatus",
            customWidth: 1,
            Cell: ({ cell }: CellProps<ITableDataItem>) => {
              return (
                <SwitchContent
                  onClick={(e) => {
                    onChangeStatus(cell.row.original.connectionId, cell.row.original.status);
                    e.preventDefault();
                  }}
                >
                  <LabeledSwitch
                    swithSize="medium"
                    id={`${cell.row.original.connectionId}`}
                    checked={cell.row.original.status === "Active" ? true : false}
                    loading={rowId === cell.row.original.connectionId && statusLoading ? true : false}
                  />
                </SwitchContent>
              );
            },
          }
        : {
            Header: <FormattedMessage id="tables.syncStatus" />,
            accessor: "latestSyncJobStatus",
            Cell: ({ cell }: CellProps<ITableDataItem>) => {
              return cell.row.original.latestSyncJobStatus === "succeeded" ? (
                <Box pl={3}>
                  {" "}
                  <Tooltip title={<FormattedMessage id="sync.successful" />} placement="top">
                    <IconButton>
                      <GreenIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : cell.row.original.latestSyncJobStatus === "running" ? (
                <Box pl={3}>
                  <Tooltip title={<FormattedMessage id="sync.running" />} placement="top">
                    <IconButton>
                      <GreenLoaderIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : cell.row.original.latestSyncJobStatus === "failed" ? (
                <Box pl={3}>
                  <Tooltip title={<FormattedMessage id="sync.failed" />} placement="top">
                    <IconButton>
                      <FailedIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : cell.row.original.latestSyncJobStatus === "waiting" ? (
                <Box pl={3}>
                  <Tooltip title={<FormattedMessage id="sync.waiting" />} placement="top">
                    <IconButton>
                      <WaitingIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : cell.row.original.latestSyncJobStatus === "disabled" ? (
                <Box pl={3}>
                  <Tooltip title={<FormattedMessage id="sync.disabled" />} placement="top">
                    <IconButton>
                      <DisabledIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : (
                <Box pl={3}>
                  <Tooltip title={<FormattedMessage id="sync.notstarted" />} placement="top">
                    <IconButton>
                      <NotStartedIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              );
            },
          },
      {
        Header: (
          <>
            <FormattedMessage id="tables.name" />
            <IconButton
              onClick={() => {
                setSortFieldName("name");
                onSortClick("name");
                setLocalSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  setSortDirection(newSortOrder);
                  setConnectorSortOrder("");
                  setEntitySortOrder("");
                  setStatusSortOrder("");
                  onSelectFilter("sortFieldName", "name", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
                  return newSortOrder;
                });
              }}
            >
              {localSortOrder === "" ? (
                <SortUpIcon />
              ) : localSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
            </IconButton>
          </>
        ),
        headerHighlighted: true,
        accessor: "name",

        Cell: ({ cell }: CellProps<ITableDataItem>) => {
          return (
            <NameColums>
              <NameCell value={cell.value} onClickRow={() => onClickRows(cell.row.original.connectionId)} />
              <NewTabIconButton id={cell.row.original.connectionId} type="Connections" />
            </NameColums>
          );
        },
      },
      // {
      //   Header: <FormattedMessage id="tables.status" />,
      //   accessor: "statusLang",
      // },

      {
        Header: (
          <>
            <FormattedMessage id="tables.source" />
            <IconButton
              onClick={() => {
                setSortFieldName("connectorName");
                onSortClick("connectorName");
                setConnectorSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  setLocalSortOrder("");
                  setEntitySortOrder("");
                  setStatusSortOrder("");
                  onSelectFilter("sortFieldName", "connectorName", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
                  return newSortOrder;
                });
              }}
            >
              {connectorSortOrder === "" ? (
                <SortUpIcon />
              ) : connectorSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
            </IconButton>
          </>
        ),
        accessor: "connectorName",
      },
      {
        Header: (
          <>
            <FormattedMessage id="tables.destination" />
            <IconButton
              onClick={() => {
                setSortFieldName("entityName");
                onSortClick("entityName");
                setEntitySortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  onSelectFilter("sortFieldName", "entityName", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
                  setLocalSortOrder("");
                  setConnectorSortOrder("");
                  setStatusSortOrder("");
                  return newSortOrder;
                });
              }}
            >
              {entitySortOrder === "" ? (
                <SortUpIcon />
              ) : entitySortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
            </IconButton>
          </>
        ),
        headerHighlighted: true,
        accessor: "entityName",
      },

      {
        Header: (
          <>
            <FormattedMessage id="tables.status" />
            <IconButton
              onClick={() => {
                setSortFieldName("status");
                onSortClick("status");
                setStatusSortOrder((prev: any) => {
                  const newSortOrder =
                    prev === "" ? SortOrderEnum.ASC : prev === SortOrderEnum.ASC ? SortOrderEnum.DESC : "";
                  setLocalSortOrder("");
                  setEntitySortOrder("");
                  setConnectorSortOrder("");
                  onSelectFilter("sortFieldName", "status", query);
                  onSelectFilter("sortDirection", newSortOrder, query);
                  return newSortOrder;
                });
              }}
            >
              {statusSortOrder === "" ? (
                <SortUpIcon />
              ) : statusSortOrder === SortOrderEnum.ASC ? (
                <SortDownIcon />
              ) : (
                <SortDescIcon />
              )}
            </IconButton>
          </>
        ),
        accessor: "status",

        Cell: ({ cell }: CellProps<ITableDataItem>) => {
          return cell.row.original.status === "active" ? (
            <FormattedMessage id="connection.active" />
          ) : (
            <FormattedMessage id="connection.inactive" />
          );
        },
      },
      {
        Header: (
          <HeaderColumns>
            <FormattedMessage id="tables.lastSyncAt" />
          </HeaderColumns>
        ),
        accessor: "latestSyncJobCreatedAt",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell timeInSecond={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: "",
        accessor: "connectionId",
        customWidth: 1,
        Cell: ({ cell }: CellProps<ITableDataItem>) => {
          return (
            <ConnectionSettingsCell
              id={cell.value}
              onClick={() => {
                onClickRows(cell.value);
              }}
            />
          );
        },
      },
    ],
    [allowSync, entity, onChangeStatus, onSync, localSortOrder, connectorSortOrder, statusSortOrder, entitySortOrder]
  );

  return <Table columns={columns} data={data} erroredRows />;
};

export default ConnectionTable;

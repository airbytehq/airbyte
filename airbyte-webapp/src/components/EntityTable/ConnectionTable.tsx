import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import { LabeledSwitch } from "components/LabeledSwitch";
import Table from "components/Table";

import { FeatureItem, useFeature } from "hooks/services/Feature";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../pages/routePaths";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
// import ConnectorCell from "./components/ConnectorCell";
// import FrequencyCell from "./components/FrequencyCell";
import LastSyncCell from "./components/LastSyncCell";
// import NameCell from "./components/NameCell";
// import SortButton from "./components/SortButton";
// import StatusCell from "./components/StatusCell";
// import SwitchButton from "./components/SwitchButton";
import { ITableDataItem, SortOrderEnum } from "./types";

const Content = styled.div`
  margin: 0 32px 0 27px;
`;

interface IProps {
  data: ITableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ITableDataItem) => void;
  onChangeStatus: (id: string) => void;
  onSync: (id: string) => void;
  rowId?: string;
  statusLoading?: boolean;
}

const ConnectionTable: React.FC<IProps> = ({ data, entity, onChangeStatus, onSync, rowId, statusLoading }) => {
  const { query, push } = useRouter();
  const allowSync = useFeature(FeatureItem.AllowSync);

  const sortBy = query.sortBy || "entityName";
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
  //       result = a[sortBy].toLowerCase().localeCompare(b[sortBy].toLowerCase());
  //     }
  //
  //     if (sortOrder === SortOrderEnum.DESC) {
  //       return -1 * result;
  //     }
  //
  //     return result;
  //   },
  //   [sortBy, sortOrder]
  // );

  // const sortingData = React.useMemo(() => data.sort(sortData), [sortData, data]);

  const onClickRows = (connectionId: string) => push(`/${RoutePaths.Connections}/${connectionId}`);

  const columns = React.useMemo(
    () => [
      {
        Header: "",
        accessor: "lastSyncStatus",
        customWidth: 1,
        Cell: ({ cell }: CellProps<ITableDataItem>) => {
          return (
            <LabeledSwitch
              id={`${cell.row.original.connectionId}`}
              checked={cell.row.original.status === "Active" ? true : false}
              onClick={() => {
                onChangeStatus(cell.row.original.connectionId);
              }}
              loading={rowId === cell.row.original.connectionId && statusLoading ? true : false}
            />
          );
        },
      },
      {
        Header: (
          <>
            <FormattedMessage id="tables.name" />
            {/* <SortButton*/}
            {/*  wasActive={sortBy === "name"}*/}
            {/*  lowToLarge={sortOrder === SortOrderEnum.ASC}*/}
            {/*  onClick={() => onSortClick("name")}*/}
            {/*/ >*/}
          </>
        ),
        headerHighlighted: true,
        accessor: "name",
        customWidth: 30,
        // Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
        //   <NameCell value={cell.value} enabled={row.original.enabled} status={row.original.lastSyncStatus} />
        // ),
      },
      {
        Header: <FormattedMessage id="tables.status" />,
        accessor: "statusLang",
        // Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
        //     <FrequencyCell value={cell.value} enabled={row.original.enabled} />
        // ),
      },
      {
        Header: (
          <>
            <FormattedMessage id="tables.lastSyncAt" />
            {/* <SortButton*/}
            {/*    wasActive={sortBy === "lastSync"}*/}
            {/*    lowToLarge={sortOrder === SortOrderEnum.ASC}*/}
            {/*    onClick={() => onSortClick("lastSync")}*/}
            {/*/ >*/}
          </>
        ),
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
          <LastSyncCell timeInSecond={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: (
          <>
            {/* {entity === "connection" ? (*/}
            <FormattedMessage id="tables.destination" />
            {/* ) : (*/}
            {/*  <FormattedMessage id={`tables.${entity}ConnectionToName`} />*/}
            {/* )}*/}
            {/* <SortButton*/}
            {/*  wasActive={sortBy === "entityName"}*/}
            {/*  lowToLarge={sortOrder === SortOrderEnum.ASC}*/}
            {/*  onClick={() => onSortClick("entityName")}*/}
            {/*/ >*/}
          </>
        ),
        headerHighlighted: true,
        accessor: "entityName",
        // Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
        //   <NameCell
        //     value={cell.value}
        //     enabled={row.original.enabled}
        //     icon={entity === "connection"}
        //     img={row.original.entityIcon}
        //   />
        // ),
      },
      {
        Header: (
          <>
            {/* {entity === "connection" ? (*/}
            <FormattedMessage id="tables.source" />
            {/* ) : (*/}
            {/*    <FormattedMessage id="tables.connector" />*/}
            {/* )}*/}
            {/* <SortButton*/}
            {/*    wasActive={sortBy === "connectorName"}*/}
            {/*    lowToLarge={sortOrder === SortOrderEnum.ASC}*/}
            {/*    onClick={() => onSortClick("connectorName")}*/}
            {/*/ >*/}
          </>
        ),
        accessor: "connectorName",
        // Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
        //     <ConnectorCell value={cell.value} enabled={row.original.enabled} img={row.original.connectorIcon} />
        // ),
      },

      // {
      //   Header: <FormattedMessage id="tables.frequency" />,
      //   accessor: "schedule",
      //   Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
      //     <FrequencyCell value={cell.value} enabled={row.original.enabled} />
      //   ),
      // },
      // {
      //   Header: <FormattedMessage id="tables.enabled" />,
      //   accessor: "enabled",
      //   customWidth: 1,
      //   Cell: ({ cell, row }: CellProps<ITableDataItem>) => (
      //     <StatusCell
      //       enabled={cell.value}
      //       id={row.original.connectionId}
      //       isSyncing={row.original.isSyncing}
      //       isManual={!row.original.schedule}
      //       onChangeStatus={onChangeStatus}
      //       onSync={onSync}
      //       allowSync={allowSync}
      //     />
      //   ),
      // },
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
    [allowSync, entity, onChangeStatus, onSync, onSortClick, sortBy, sortOrder]
  );

  return (
    <Content>
      <Table
        columns={columns}
        data={data}
        // onClickRow={onClickRow}
        erroredRows
      />
    </Content>
  );
};

export default ConnectionTable;

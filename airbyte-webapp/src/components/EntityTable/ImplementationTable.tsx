import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import Table from "components/Table";

// import { useCloneDestination } from "hooks/services/useDestinationHook";
// import { useCloneSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";

// import { SourceCloneRequestBody, DestinationCloneRequestBody } from "../../core/request/AirbyteClient";
import { RoutePaths } from "../../pages/routePaths";
import AllConnectionsStatusCell from "./components/AllConnectionsStatusCell";
import ConnectEntitiesCell from "./components/ConnectEntitiesCell";
import ConnectionCopyCell from "./components/ConnectionCopyCell";
import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import ConnectorCell from "./components/ConnectorCell";
import LastSyncCell from "./components/LastSyncCell";
import NameCell from "./components/NameCell";
import SortButton from "./components/SortButton";
import styles from "./ImplementationTable.module.scss";
import { EntityTableDataItem, SortOrderEnum } from "./types";
// import { useGetSource } from "hooks/services/useSourceHook";
// import { useSourceDefinition } from "services/connector/SourceDefinitionService";

interface IProps {
  data: EntityTableDataItem[];
  entity: "source" | "destination";
  onClickRow?: (data: EntityTableDataItem) => void;
}

const ImplementationTable: React.FC<IProps> = ({ data, entity }) => {
  const { query, push } = useRouter();
  const sortBy = query.sortBy || "entity";
  const sortOrder = query.order || SortOrderEnum.ASC;
  // const source = useGetSource();

  // const { mutateAsync: cloneSource } = useCloneSource();
  // const { mutateAsync: cloneDestination } = useCloneDestination();

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

  const sortData = useCallback(
    (a, b) => {
      let result;
      if (sortBy === "lastSync") {
        result = b[sortBy] - a[sortBy];
      } else {
        result = a[`${sortBy}Name`].toLowerCase().localeCompare(b[`${sortBy}Name`].toLowerCase());
      }

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const routerPath = entity === "source" ? RoutePaths.Source : RoutePaths.Destination;
  const clickEditRow = (entityId: string) => push(`/${routerPath}/${entityId}`);

  const sortingData = React.useMemo(() => data.sort(sortData), [sortData, data]);

  // const copySourceRow = async (entityId: string) => {
  //   const cloneSourceData: SourceCloneRequestBody = {
  //     sourceCloneId: entityId,
  //   };
  //   await cloneSource({ source: cloneSourceData });
  // };

  // const copyDestinationRow = async (entityId: string) => {
  //   const cloneDestinationRow: DestinationCloneRequestBody = {
  //     destinationCloneId: entityId,
  //   };
  //   await cloneDestination({ destination: cloneDestinationRow });
  // };

  const clickCopyRow = (entityId: string) => {
    // if (entity === "source") {
    // const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);
    push(`${entityId}/copy`, {});
    // }

    // entity === "source" ? copySourceRow(entityId) : copyDestinationRow(entityId);
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
        accessor: "entityName",
        customWidth: 40,
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <NameCell value={cell.value} enabled={row.original.enabled} />
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
        accessor: "connectorName",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectorCell value={cell.value} enabled={row.original.enabled} img={row.original.connectorIcon} />
        ),
      },
      {
        Header: <FormattedMessage id={`tables.${entity}ConnectWith`} />,
        accessor: "connectEntities",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <ConnectEntitiesCell values={cell.value} entity={entity} enabled={row.original.enabled} />
        ),
      },
      {
        Header: (
          <div className={styles.headerColumns}>
            <FormattedMessage id="tables.lastSync" />
            <SortButton
              wasActive={sortBy === "lastSync"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("lastSync")}
            />
          </div>
        ),
        // customWidth:20,
        accessor: "lastSync",
        Cell: ({ cell, row }: CellProps<EntityTableDataItem>) => (
          <LastSyncCell timeInSecond={cell.value} enabled={row.original.enabled} />
        ),
      },
      {
        Header: <FormattedMessage id="sources.status" />,
        id: "status",
        accessor: "connectEntities",
        Cell: ({ cell }: CellProps<EntityTableDataItem>) => <AllConnectionsStatusCell connectEntities={cell.value} />,
      },
      {
        Header: <FormattedMessage id="sources.editText" />,
        id: "edit",
        accessor: "entityId",
        Cell: ({ cell }: CellProps<EntityTableDataItem>) => (
          <ConnectionSettingsCell id={cell.value} onClick={() => clickEditRow(cell.value)} />
        ),
      },
      {
        Header: <FormattedMessage id="sources.copyText" />,
        id: "copy",
        accessor: "entityId",
        Cell: ({ cell }: CellProps<EntityTableDataItem>) => (
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
      <Table
        columns={columns}
        data={sortingData}
        //  onClickRow={onClickRow}
        erroredRows
      />
    </div>
  );
};

export default ImplementationTable;

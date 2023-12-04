import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import styled from "styled-components";

import Table from "components/Table";

import useRouter from "hooks/useRouter";

import ConnectionSettingsCell from "./components/ConnectionSettingsCell";
import NameCell from "./components/NameCell";
import NewTabIconButton from "./components/NewTabIconButton";
import { ITableDataItem } from "./types";
import { RoutePaths } from "../../pages/routePaths";

const NameColums = styled.div`
  display: flex;
  aligin-items: center;
`;

interface IProps {
  data: ITableDataItem[];
  entity: "source" | "destination" | "connection";
  onClickRow?: (data: ITableDataItem) => void;
}
//
const NewItemTable: React.FC<IProps> = ({ data, entity }) => {
  const { push } = useRouter();

  const onClickRows = (connectionId: string) => push(`/${RoutePaths.Connections}/${connectionId}`);

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="tables.name" />,
        headerHighlighted: true,
        accessor: "name",
        customWidth: 30,
        Cell: ({ cell }: CellProps<ITableDataItem>) => {
          return (
            <NameColums>
              <NameCell value={cell.value} onClickRow={() => onClickRows(cell.row.original.connectionId)} />
              <NewTabIconButton id={cell.row.original.connectionId} type="Connections" />
            </NameColums>
          );
        },
      },
      {
        Header: <FormattedMessage id="tables.status" />,
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
        Header: <FormattedMessage id="tables.source" />,
        accessor: "connectorName",
      },
      {
        Header: <FormattedMessage id="tables.destination" />,
        headerHighlighted: true,
        accessor: "entityName",
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
    [entity]
  );

  return <Table columns={columns} data={data} erroredRows />;
};

export default NewItemTable;

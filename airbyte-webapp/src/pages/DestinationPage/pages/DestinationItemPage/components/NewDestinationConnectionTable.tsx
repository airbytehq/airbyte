import React from "react";

import NewItemTable from "components/EntityTable/NewItemTable";
import { ITableDataItem } from "components/EntityTable/types";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

interface IProps {
  connections: any;
}

const NewDestinationConnectionTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const clickRow = (destination: ITableDataItem) =>
    push(`../../../${RoutePaths.Connections}/${destination.connectionId}`);

  return <NewItemTable data={connections} onClickRow={clickRow} entity="destination" />;
};

export default NewDestinationConnectionTable;

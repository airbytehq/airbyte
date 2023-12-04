import React from "react";

import NewItemTable from "components/EntityTable/NewItemTable";
import { ITableDataItem } from "components/EntityTable/types";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

interface IProps {
  connections: any;
}

const NewSourceConnectionTable: React.FC<IProps> = ({ connections }) => {
  const { push } = useRouter();
  const clickRow = (source: ITableDataItem) => push(`../../../${RoutePaths.Connections}/${source.connectionId}`);

  return <NewItemTable data={connections} onClickRow={clickRow} entity="source" />;
};

export default NewSourceConnectionTable;

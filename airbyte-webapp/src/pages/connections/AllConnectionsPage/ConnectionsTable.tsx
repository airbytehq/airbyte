import React from "react";
import { useNavigate } from "react-router-dom";

import { ConnectionTable } from "components/EntityTable";
import { ConnectionTableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";

interface IProps {
  connections: WebBackendConnectionListItem[];
}

const ConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const navigate = useNavigate();

  const data = getConnectionTableData(connections, "connection");

  const clickRow = (source: ConnectionTableDataItem) => navigate(`${source.connectionId}`);

  return <ConnectionTable data={data} onClickRow={clickRow} entity="connection" />;
};

export default ConnectionsTable;

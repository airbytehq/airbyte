import React from "react";
import { useNavigate } from "react-router-dom";

import { ConnectionTable } from "components/EntityTable";
import { ConnectionTableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { RoutePaths } from "pages/routePaths";

import styles from "./SourceConnectionTable.module.scss";

interface IProps {
  connections: WebBackendConnectionListItem[];
}

const SourceConnectionTable: React.FC<IProps> = ({ connections }) => {
  const navigate = useNavigate();

  const data = getConnectionTableData(connections, "source");

  const clickRow = (source: ConnectionTableDataItem) =>
    navigate(`../../../${RoutePaths.Connections}/${source.connectionId}`);

  return (
    <div className={styles.content}>
      <ConnectionTable data={data} onClickRow={clickRow} entity="source" />
    </div>
  );
};

export default SourceConnectionTable;

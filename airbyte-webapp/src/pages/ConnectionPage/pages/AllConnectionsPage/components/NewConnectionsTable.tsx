import React, { useState } from "react";
import styled from "styled-components";

import { ConnectionTable } from "components/EntityTable";
import { ITableDataItem } from "components/EntityTable/types";

import useRouter from "hooks/useRouter";

import { WebBackendNewConnectionList } from "../../../../../core/request/AirbyteClient";

const Content = styled.div`
  padding: 0 24px 30px 24px;
`;

interface IProps {
  connections: WebBackendNewConnectionList[];
  onSetMessageId: (id: string) => void;
}

const NewConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const [rowId] = useState<string>("");

  const { push } = useRouter();

  const clickRow = (source: ITableDataItem) => push(`${source.connectionId}`);

  return (
    <Content>
      <ConnectionTable data={connections as any} onClickRow={clickRow} entity="connection" rowId={rowId} />
    </Content>
  );
};

export default NewConnectionsTable;

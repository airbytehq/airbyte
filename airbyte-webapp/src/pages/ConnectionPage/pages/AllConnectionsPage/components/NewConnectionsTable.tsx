import React, { useEffect, useState } from "react";
import styled from "styled-components";

import { ConnectionTable } from "components/EntityTable";
import { ITableDataItem } from "components/EntityTable/types";

import { getUser } from "core/AuthContext";
import useRouter from "hooks/useRouter";

import {
  WebBackendNewConnectionList,
  WebBackendNewConnectionStatusList,
} from "../../../../../core/request/AirbyteClient";

const Content = styled.div`
  padding: 0 24px 30px 24px;
`;

interface IProps {
  connections?: WebBackendNewConnectionList[];
  connectionStatus?: WebBackendNewConnectionStatusList[];
  onSetMessageId: (id: string) => void;
}

const NewConnectionsTable: React.FC<IProps> = ({ connections }) => {
  const [statusList, setStatusList] = useState([]);
  const user = getUser();
  const connectionIds = connections?.map((con: any) => con?.connectionId);

  const apiData = {
    connectionIds,
  };
  useEffect(() => {
    const fetchConnectionStatus = async () => {
      try {
        // Check if connections array is not empty before making the API call
        if (connections && connections?.length > 0) {
          const apiUrl = `${process.env.REACT_APP_API_URL}/etl/web_backend/connections/status`;

          const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `${user?.token}`,
            },
            body: JSON.stringify(apiData),
          });

          const responseData = await response.json();
          setStatusList(responseData.connectionStatusList);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchConnectionStatus();
  }, [connections]);
  const updatedConnections = connections?.map((conn) => {
    const matchingStatus = statusList?.find((status: any) => status?.connectionId === conn?.connectionId);
    return { ...conn, ...(matchingStatus || {}) };
  });

  const [rowId] = useState<string>("");

  const { push } = useRouter();

  const clickRow = (source: ITableDataItem) => push(`${source.connectionId}`);

  return (
    <Content>
      <ConnectionTable data={updatedConnections as any} onClickRow={clickRow} entity="connection" rowId={rowId} />
    </Content>
  );
};

export default NewConnectionsTable;

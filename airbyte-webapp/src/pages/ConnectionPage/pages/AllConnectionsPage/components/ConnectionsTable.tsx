import React, { useCallback, useState } from "react";
import { useQueryClient } from "react-query";
import styled from "styled-components";

import { ConnectionTable } from "components/EntityTable";
import useSyncActions from "components/EntityTable/hooks";
import { ITableDataItem } from "components/EntityTable/types";
import { getConnectionTableData } from "components/EntityTable/utils";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { invalidateConnectionsList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import { WebBackendConnectionRead } from "../../../../../core/request/AirbyteClient";

const Content = styled.div`
  padding: 0 24px 30px 24px;
`;

interface IProps {
  connections: WebBackendConnectionRead[];
  onSetMessageId: (id: string) => void;
}

const ConnectionsTable: React.FC<IProps> = ({ connections, onSetMessageId }) => {
  const [rowId, setRowID] = useState<string>("");
  const [statusLoading, setStatusLoading] = useState<boolean>(false);
  const { push } = useRouter();
  const { changeStatus, syncManualConnection } = useSyncActions();
  const queryClient = useQueryClient();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const { sourceDefinitions } = useSourceDefinitionList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getConnectionTableData(connections, sourceDefinitions, destinationDefinitions, "connection");

  // const onChangeStatus = useCallback(
  //   async (connectionId: string) => {
  //     const connection = connections.find((item) => item.connectionId === connectionId);

  //     if (connection) {
  //       setRowID(connectionId);
  //       setStatusLoading(true);
  //       await changeStatus(connection);
  //       await invalidateConnectionsList(queryClient);
  //       setRowID("");
  //       setStatusLoading(false);
  //     }
  //   },
  //   [changeStatus, connections, queryClient]
  // );

  const updateStatus = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);
      if (connection) {
        setRowID(connectionId);
        setStatusLoading(true);
        await changeStatus(connection);
        await invalidateConnectionsList(queryClient);
        setRowID("");
        setStatusLoading(false);
        onSetMessageId(
          connection.status === "active" ? "tables.connection.disabled.text" : "tables.connection.enabled.text"
        );
      }
    },
    [changeStatus, connections, queryClient]
  );

  const onChangeStatus = (connectionId: string, status: string) => {
    if (status === "Inactive") {
      updateStatus(connectionId);
      return;
    }
    openConfirmationModal({
      title: "tables.connection.modal.disabled.title",
      text: "tables.connection.modal.disabled.text",
      submitButtonText: "tables.connection.modal.button.disable",
      onSubmit: () => {
        closeConfirmationModal();
        updateStatus(connectionId);
      },
    });
  };

  const onSync = useCallback(
    async (connectionId: string) => {
      const connection = connections.find((item) => item.connectionId === connectionId);
      if (connection) {
        await syncManualConnection(connection);
      }
    },
    [connections, syncManualConnection]
  );

  const clickRow = (source: ITableDataItem) => push(`${source.connectionId}`);

  return (
    <Content>
      <ConnectionTable
        data={data}
        onClickRow={clickRow}
        entity="connection"
        onChangeStatus={onChangeStatus}
        onSync={onSync}
        rowId={rowId}
        statusLoading={statusLoading}
      />
    </Content>
  );
};

export default ConnectionsTable;

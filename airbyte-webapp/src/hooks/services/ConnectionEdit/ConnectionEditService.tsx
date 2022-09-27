import { useContext, useState, createContext, useCallback } from "react";
import { useAsyncFn } from "react-use";

import { ConnectionStatus, WebBackendConnectionUpdate } from "core/request/AirbyteClient";

import { ConnectionFormServiceProvider } from "../ConnectionForm/ConnectionFormService";
import { useGetConnection, useUpdateConnection, useWebConnectionService } from "../useConnectionHook";

interface ConnectionEditProps {
  connectionId: string;
}

const useConnectionEdit = ({ connectionId }: ConnectionEditProps) => {
  const [connection, setConnection] = useState(useGetConnection(connectionId));
  const connectionService = useWebConnectionService();
  const [schemaHasBeenRefreshed, setSchemaHasBeenRefreshed] = useState(false);

  const [{ loading: schemaRefreshing }, refreshSchema] = useAsyncFn(async () => {
    setConnection(await connectionService.getConnection(connectionId, true));
    setSchemaHasBeenRefreshed(true);
  }, [connectionId]);

  const { mutateAsync: updateConnectionAction, isLoading: connectionUpdating } = useUpdateConnection();

  const updateConnection = useCallback(
    async (connection: WebBackendConnectionUpdate) => {
      // TODO: Check if the form is dirty before firing off an update action
      setConnection(await updateConnectionAction(connection));
    },
    [updateConnectionAction]
  );

  return {
    connection,
    connectionUpdating,
    schemaRefreshing,
    schemaHasBeenRefreshed,
    updateConnection,
    setSchemaHasBeenRefreshed,
    refreshSchema,
  };
};

const ConnectionEditContext = createContext<Omit<ReturnType<typeof useConnectionEdit>, "refreshSchema"> | null>(null);

export const ConnectionEditServiceProvider: React.FC<ConnectionEditProps> = ({ children, ...props }) => {
  const { refreshSchema, ...data } = useConnectionEdit(props);
  return (
    <ConnectionEditContext.Provider value={data}>
      <ConnectionFormServiceProvider
        mode={data.connection.status === ConnectionStatus.deprecated ? "readonly" : "edit"}
        connection={data.connection}
        refreshSchema={refreshSchema}
      >
        {children}
      </ConnectionFormServiceProvider>
    </ConnectionEditContext.Provider>
  );
};

export const useConnectionEditService = () => {
  const context = useContext(ConnectionEditContext);
  if (context === null) {
    throw new Error("useConnectionEditService must be used within a ConnectionEditServiceProvider");
  }
  return context;
};

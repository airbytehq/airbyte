import { useContext, useState, createContext, useCallback } from "react";
import { useAsyncFn } from "react-use";

import { ConnectionStatus, WebBackendConnectionUpdate } from "core/request/AirbyteClient";

import { ConnectionFormServiceProvider } from "../ConnectionForm/ConnectionFormService";
import { useGetConnection, useUpdateConnection, useWebConnectionService } from "../useConnectionHook";
import { SchemaError } from "../useSourceHook";

interface ConnectionEditProps {
  connectionId: string;
}

const useConnectionEdit = ({ connectionId }: ConnectionEditProps) => {
  const [connection, setConnection] = useState(useGetConnection(connectionId));
  const connectionService = useWebConnectionService();
  const [schemaHasBeenRefreshed, setSchemaHasBeenRefreshed] = useState(false);

  const [{ loading: schemaRefreshing, error: schemaError }, refreshSchema] = useAsyncFn(async () => {
    const refreshedConnection = await connectionService.getConnection(connectionId, true);
    setConnection(refreshedConnection);
    setSchemaHasBeenRefreshed(true);
  }, [connectionId]);

  const { mutateAsync: updateConnectionAction, isLoading: connectionUpdating } = useUpdateConnection();

  const updateConnection = useCallback(
    async (connection: WebBackendConnectionUpdate) => {
      setConnection(await updateConnectionAction(connection));
    },
    [updateConnectionAction]
  );

  return {
    connection,
    connectionUpdating,
    schemaError,
    schemaRefreshing,
    schemaHasBeenRefreshed,
    updateConnection,
    setSchemaHasBeenRefreshed,
    refreshSchema,
  };
};

const ConnectionEditContext = createContext<Omit<
  ReturnType<typeof useConnectionEdit>,
  "refreshSchema" | "schemaError"
> | null>(null);

export const ConnectionEditServiceProvider: React.FC<React.PropsWithChildren<ConnectionEditProps>> = ({
  children,
  ...props
}) => {
  const { refreshSchema, schemaError, ...data } = useConnectionEdit(props);
  return (
    <ConnectionEditContext.Provider value={data}>
      <ConnectionFormServiceProvider
        mode={data.connection.status === ConnectionStatus.deprecated ? "readonly" : "edit"}
        connection={data.connection}
        schemaError={schemaError as SchemaError}
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

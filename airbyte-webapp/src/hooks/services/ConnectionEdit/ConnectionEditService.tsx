import { useContext, useState, createContext, useCallback } from "react";
import { useAsyncFn } from "react-use";

import { ConnectionStatus, WebBackendConnectionRead, WebBackendConnectionUpdate } from "core/request/AirbyteClient";
import { equal } from "utils/objects";

import { ConnectionFormServiceProvider } from "../ConnectionForm/ConnectionFormService";
import { useGetConnection, useUpdateConnection, useWebConnectionService } from "../useConnectionHook";
import { SchemaError } from "../useSourceHook";

interface ConnectionEditProps {
  connectionId: string;
}

const useConnectionEdit = ({ connectionId }: ConnectionEditProps) => {
  const connectionService = useWebConnectionService();
  const [connection, setConnection] = useState(useGetConnection(connectionId));
  const [refreshedConnection, setRefreshedConnection] = useState<WebBackendConnectionRead>();
  const [schemaHasBeenRefreshed, setSchemaHasBeenRefreshed] = useState(false);

  const [{ loading: schemaRefreshing, error: schemaError }, refreshSchema] = useAsyncFn(async () => {
    const refreshedConnection = await connectionService.getConnection(connectionId, true);
    const hasCatalogChanged = !equal(
      connection.syncCatalog.streams.filter((s) => s.config?.selected),
      refreshedConnection.syncCatalog.streams.filter((s) => s.config?.selected)
    );
    if (hasCatalogChanged) {
      setRefreshedConnection(refreshedConnection);
      setSchemaHasBeenRefreshed(true);
    } else {
      setConnection(refreshedConnection);
    }
  }, [connectionId, connection]);

  const { mutateAsync: updateConnectionAction, isLoading: connectionUpdating } = useUpdateConnection();

  const clearRefreshedSchema = useCallback(() => {
    setRefreshedConnection(undefined);
    setSchemaHasBeenRefreshed(false);
  }, []);

  const updateConnection = useCallback(
    async (connection: WebBackendConnectionUpdate) => {
      setConnection(await updateConnectionAction(connection));
      clearRefreshedSchema();
    },
    [clearRefreshedSchema, updateConnectionAction]
  );

  return {
    connection: refreshedConnection ?? connection,
    connectionUpdating,
    schemaError,
    schemaRefreshing,
    schemaHasBeenRefreshed,
    updateConnection,
    refreshSchema,
    clearRefreshedSchema,
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

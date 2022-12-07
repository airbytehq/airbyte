import isEqual from "lodash/isEqual";
import pick from "lodash/pick";
import { useContext, useState, createContext, useCallback } from "react";
import { useAsyncFn } from "react-use";

import {
  AirbyteCatalog,
  AirbyteStreamConfiguration,
  ConnectionStatus,
  WebBackendConnectionRead,
  WebBackendConnectionUpdate,
} from "core/request/AirbyteClient";

import { ConnectionFormServiceProvider } from "../ConnectionForm/ConnectionFormService";
import { useGetConnection, useUpdateConnection, useWebConnectionService } from "../useConnectionHook";
import { SchemaError } from "../useSourceHook";

interface ConnectionEditProps {
  connectionId: string;
}

export interface ConnectionCatalog {
  syncCatalog: AirbyteCatalog;
  catalogId?: string;
}

interface ConnectionEditHook {
  connection: WebBackendConnectionRead;
  connectionUpdating: boolean;
  schemaError?: Error;
  schemaRefreshing: boolean;
  schemaHasBeenRefreshed: boolean;
  updateConnection: (connectionUpdates: WebBackendConnectionUpdate) => Promise<void>;
  refreshSchema: () => Promise<void>;
  discardRefreshedSchema: () => void;
}

const getConnectionCatalog = (connection: WebBackendConnectionRead): ConnectionCatalog =>
  pick(connection, ["syncCatalog", "catalogId"]);

export const getConnectionWithUpdatedCursorAndPrimaryKey = (
  connection: WebBackendConnectionRead
): WebBackendConnectionRead => {
  const newConnection = { ...connection };
  connection.catalogDiff?.transforms.forEach((transform) => {
    const syncCatalogItemIndex = connection.syncCatalog.streams.findIndex(
      (stream) => stream.stream?.name === transform.streamDescriptor.name
    );
    if (syncCatalogItemIndex === -1) {
      return;
    }
    const syncCatalogItem = connection.syncCatalog.streams[syncCatalogItemIndex];
    if (transform.transformType === "update_stream") {
      transform.updateStream?.forEach((updateStream) => {
        if (updateStream.transformType !== "remove_field") {
          return;
        }
        const updatedStream = { ...connection.syncCatalog.streams[syncCatalogItemIndex] };
        const isPkRemoved = syncCatalogItem.config?.primaryKey?.some((pk) => isEqual(updateStream.fieldName, pk));
        const isCursorRemoved = isEqual(updateStream.fieldName, syncCatalogItem.config?.cursorField);
        if (isPkRemoved || isCursorRemoved) {
          if (connection.syncCatalog.streams[syncCatalogItemIndex].config) {
            updatedStream.config = {
              ...(connection.syncCatalog.streams[syncCatalogItemIndex].config as AirbyteStreamConfiguration),
            };
            if (isCursorRemoved) {
              updatedStream.config.cursorField = [];
            }
            if (isPkRemoved) {
              updatedStream.config.primaryKey = [];
            }
          }
          newConnection.syncCatalog = {
            ...connection.syncCatalog,
            streams: [
              ...connection.syncCatalog.streams?.slice(0, syncCatalogItemIndex),
              updatedStream,
              ...connection.syncCatalog.streams?.slice(syncCatalogItemIndex + 1),
            ],
          };
        }
      });
    }
  });
  return newConnection;
};

const useConnectionEdit = ({ connectionId }: ConnectionEditProps): ConnectionEditHook => {
  const connectionService = useWebConnectionService();
  const [connection, setConnection] = useState(useGetConnection(connectionId));
  const [catalog, setCatalog] = useState<ConnectionCatalog>(() => getConnectionCatalog(connection));
  const [schemaHasBeenRefreshed, setSchemaHasBeenRefreshed] = useState(false);

  const [{ loading: schemaRefreshing, error: schemaError }, refreshSchema] = useAsyncFn(async () => {
    const refreshedConnection = await connectionService.getConnection(connectionId, true);
    if (refreshedConnection.catalogDiff && refreshedConnection.catalogDiff.transforms?.length > 0) {
      const updatedConnection = getConnectionWithUpdatedCursorAndPrimaryKey(refreshedConnection);
      setConnection(updatedConnection);
      setSchemaHasBeenRefreshed(true);
    }
  }, [connectionId]);

  const discardRefreshedSchema = useCallback(() => {
    setConnection((connection) => ({
      ...connection,
      ...catalog,
      catalogDiff: undefined,
    }));
    setSchemaHasBeenRefreshed(false);
  }, [catalog]);

  const { mutateAsync: updateConnectionAction, isLoading: connectionUpdating } = useUpdateConnection();

  const updateConnection = useCallback(
    async (connectionUpdates: WebBackendConnectionUpdate) => {
      const updatedConnection = await updateConnectionAction(connectionUpdates);
      const updatedKeys = Object.keys(connectionUpdates).map((key) => (key === "sourceCatalogId" ? "catalogId" : key));
      const connectionPatch = pick(updatedConnection, updatedKeys);
      const wasSyncCatalogUpdated = !!connectionPatch.syncCatalog;

      // Ensure that the catalog diff cleared and that the schemaChange status has been updated
      const syncCatalogUpdates: Partial<WebBackendConnectionRead> | undefined = wasSyncCatalogUpdated
        ? {
            catalogDiff: undefined,
            schemaChange: updatedConnection.schemaChange,
          }
        : undefined;

      // Mutate the current connection state only with the values that were updated
      setConnection((connection) => ({
        ...connection,
        ...connectionPatch,
        ...syncCatalogUpdates,
      }));

      if (wasSyncCatalogUpdated) {
        // The catalog ws also saved, so update the current catalog
        setCatalog(getConnectionCatalog(updatedConnection));
        setSchemaHasBeenRefreshed(false);
      }
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
    refreshSchema,
    discardRefreshedSchema,
  };
};

const ConnectionEditContext = createContext<Omit<ConnectionEditHook, "refreshSchema" | "schemaError"> | null>(null);

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

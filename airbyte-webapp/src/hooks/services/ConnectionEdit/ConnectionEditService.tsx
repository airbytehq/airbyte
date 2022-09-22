import { useContext, useState, createContext } from "react";
import { useAsyncFn } from "react-use";

import { ConnectionFormServiceProvider } from "../ConnectionForm/ConnectionFormService";
import { useGetConnection, useWebConnectionService } from "../useConnectionHook";

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

  return {
    connection,
    schemaRefreshing,
    schemaHasBeenRefreshed,
    setConnection,
    setSchemaHasBeenRefreshed,
    refreshSchema,
  };
};

const ConnectionEditContext = createContext<ReturnType<typeof useConnectionEdit> | null>(null);

export const ConnectionEditServiceProvider: React.FC<ConnectionEditProps> = ({ children, ...props }) => {
  const data = useConnectionEdit(props);
  // TODO: Mode needs to be able to be set to 'readonly'
  return (
    <ConnectionEditContext.Provider value={data}>
      <ConnectionFormServiceProvider mode="edit" connection={data.connection}>
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

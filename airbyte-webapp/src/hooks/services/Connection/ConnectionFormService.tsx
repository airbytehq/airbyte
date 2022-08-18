// import { useDiscoverSchema } from "../useSourceHook";

import React, { createContext, useContext } from "react";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";
import { useInitialValues } from "views/Connection/ConnectionForm/formConfig";

interface ConnectionServiceProps {
  connection:
    | WebBackendConnectionRead
    | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);
  mode: ConnectionFormMode;
}

const useConnectionForm = ({ connection, mode }: ConnectionServiceProps) => {
  // Need to track form dirty state
  // Might be easy if form context is in here

  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);

  const initialValues = useInitialValues(connection, destDefinition, mode !== "create");

  return { initialValues, destDefinition, connection, mode };
};

const ConnectionFormContext = createContext<ReturnType<typeof useConnectionForm> | null>(null);

export const ConnectionFormProvider: React.FC<ConnectionServiceProps> = ({ children, ...props }) => {
  const data = useConnectionForm(props);
  return <ConnectionFormContext.Provider value={data}>{children}</ConnectionFormContext.Provider>;
};

export const useConnectionFormService = () => {
  const context = useContext(ConnectionFormContext);
  if (context === null) {
    throw new Error("useConnectionFormService must be used within a ConnectionFormProvider");
  }
  return context;
};

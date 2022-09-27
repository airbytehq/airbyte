import React, { createContext, useCallback, useContext, useState } from "react";
import { useIntl } from "react-intl";

import { OperationRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { FormError, generateMessageFromError } from "utils/errorStatusMessage";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { ValuesProps } from "../useConnectionHook";

export type ConnectionFormMode = "create" | "edit" | "readonly";

export type ConnectionOrPartialConnection =
  | WebBackendConnectionRead
  | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);

export interface ConnectionServiceProps {
  connection: ConnectionOrPartialConnection;
  mode: ConnectionFormMode;
  refreshSchema: () => void;
}

export const tidyConnectionFormValues = (
  values: FormikConnectionFormValues,
  workspaceId: string,
  operations?: OperationRead[]
): ValuesProps => {
  // TODO: We should try to fix the types so we don't need the casting.
  const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
    context: { isRequest: true },
  }) as unknown as ConnectionFormValues;

  formValues.operations = mapFormPropsToOperation(values, operations, workspaceId);

  return formValues;
};

const useConnectionForm = ({ connection, mode, refreshSchema }: ConnectionServiceProps) => {
  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const initialValues = useInitialValues(connection, destDefinition);
  const { formatMessage } = useIntl();
  const [submitError, setSubmitError] = useState<FormError | null>(null);

  const getErrorMessage = useCallback(
    (formValid: boolean, connectionDirty: boolean) =>
      submitError
        ? generateMessageFromError(submitError)
        : connectionDirty && !formValid
        ? formatMessage({ id: "connectionForm.validation.error" })
        : null,
    [formatMessage, submitError]
  );

  return {
    connection,
    mode,
    destDefinition,
    initialValues,
    setSubmitError,
    getErrorMessage,
    refreshSchema,
  };
};

const ConnectionFormContext = createContext<ReturnType<typeof useConnectionForm> | null>(null);

export const ConnectionFormServiceProvider: React.FC<ConnectionServiceProps> = ({ children, ...props }) => {
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

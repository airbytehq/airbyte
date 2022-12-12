import React, { createContext, useCallback, useContext, useState } from "react";
import { useIntl } from "react-intl";

import {
  ConnectionScheduleType,
  DestinationDefinitionSpecificationRead,
  OperationRead,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { FormError, generateMessageFromError } from "utils/errorStatusMessage";
import {
  ConnectionFormValues,
  createConnectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { useUniqueFormId } from "../FormChangeTracker";
import { ValuesProps } from "../useConnectionHook";
import { SchemaError } from "../useSourceHook";

export type ConnectionFormMode = "create" | "edit" | "readonly";

export type ConnectionOrPartialConnection =
  | WebBackendConnectionRead
  | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);

interface ConnectionServiceProps {
  connection: ConnectionOrPartialConnection;
  mode: ConnectionFormMode;
  schemaError?: SchemaError | null;
  refreshSchema: () => Promise<void>;
}

export const tidyConnectionFormValues = (
  values: FormikConnectionFormValues,
  workspaceId: string,
  mode: ConnectionFormMode,
  allowSubOneHourCronExpressions: boolean,
  isAutoDetectSchemaChangesEnabled: boolean,
  operations?: OperationRead[]
): ValuesProps => {
  // TODO (https://github.com/airbytehq/airbyte/issues/17279): We should try to fix the types so we don't need the casting.
  const formValues: ConnectionFormValues = createConnectionValidationSchema({
    mode,
    allowSubOneHourCronExpressions,
    isAutoDetectSchemaChangesEnabled,
  }).cast(values, {
    context: { isRequest: true },
  }) as unknown as ConnectionFormValues;

  formValues.operations = mapFormPropsToOperation(values, operations, workspaceId);

  if (formValues.scheduleType === ConnectionScheduleType.manual) {
    // Have to set this to undefined to override the existing scheduleData
    formValues.scheduleData = undefined;
  }
  return formValues;
};

interface ConnectionFormHook {
  connection: ConnectionOrPartialConnection;
  mode: ConnectionFormMode;
  destDefinition: DestinationDefinitionSpecificationRead;
  initialValues: FormikConnectionFormValues;
  schemaError?: SchemaError;
  formId: string;
  setSubmitError: (submitError: FormError | null) => void;
  getErrorMessage: (formValid: boolean, connectionDirty: boolean) => string | JSX.Element | null;
  refreshSchema: () => Promise<void>;
}

const useConnectionForm = ({
  connection,
  mode,
  schemaError,
  refreshSchema,
}: ConnectionServiceProps): ConnectionFormHook => {
  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const initialValues = useInitialValues(connection, destDefinition, mode !== "create");
  const { formatMessage } = useIntl();
  const [submitError, setSubmitError] = useState<FormError | null>(null);
  const formId = useUniqueFormId();

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
    schemaError,
    formId,
    setSubmitError,
    getErrorMessage,
    refreshSchema,
  };
};

const ConnectionFormContext = createContext<ConnectionFormHook | null>(null);

export const ConnectionFormServiceProvider: React.FC<React.PropsWithChildren<ConnectionServiceProps>> = ({
  children,
  ...props
}) => {
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

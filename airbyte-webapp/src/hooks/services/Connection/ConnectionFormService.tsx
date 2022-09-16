import React, { createContext, useContext, useMemo, useState } from "react";
import { useAsyncFn } from "react-use";

import { ConnectionScheduleType, OperationRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { useChangedFormsById } from "../FormChangeTracker";
import { ValuesProps } from "../useConnectionHook";

export type ConnectionOrPartialConnection =
  | WebBackendConnectionRead
  | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);

export interface SubmitCancel {
  submitCancel: boolean;
}
export type SubmitResult = WebBackendConnectionRead | SubmitCancel;

export interface ConnectionServiceProps {
  connection: WebBackendConnectionRead;
  schemaHasBeenRefreshed: boolean;
  mode: ConnectionFormMode;
  formId: string;
  setConnection: (connection: WebBackendConnectionRead) => void;
  setSchemaHasBeenRefreshed: (refreshed: boolean) => void;
  onSubmit?: (values: ValuesProps) => Promise<SubmitResult>;
  onAfterSubmit?: (submitResult: SubmitResult) => void;
  refreshCatalog: () => Promise<void>;
}

export function isSubmitCancel(submitResult: SubmitResult): submitResult is { submitCancel: boolean } {
  return submitResult.hasOwnProperty("submitCancel");
}

export const tidyConnectionFormValues = (
  values: FormikConnectionFormValues,
  operations: OperationRead[] | undefined,
  workspaceId: string
): ValuesProps => {
  // Set the scheduleType based on the schedule value
  // TODO: I think this should be removed
  values["scheduleType"] = values.scheduleData?.basicSchedule
    ? ConnectionScheduleType.basic
    : ConnectionScheduleType.manual;

  // TODO: We should align these types
  // With the PATCH-style endpoint available we might be able to forego this pattern
  const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
    context: { isRequest: true },
  }) as unknown as ConnectionFormValues;

  formValues.operations = mapFormPropsToOperation(values, operations, workspaceId);

  return formValues;
};

const useConnectionForm = ({
  connection,
  mode,
  formId,
  schemaHasBeenRefreshed,
  onAfterSubmit,
  setConnection,
  setSchemaHasBeenRefreshed,
  refreshCatalog,
}: ConnectionServiceProps) => {
  const [submitError, setSubmitError] = useState<Error | null>(null);

  const [{ loading: isRefreshingCatalog }, refreshConnectionCatalog] = useAsyncFn(refreshCatalog, []);

  const [changedFormsById] = useChangedFormsById();
  const connectionDirty = useMemo(() => !!changedFormsById?.[formId], [changedFormsById, formId]);

  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const initialValues = useInitialValues(connection, destDefinition, mode !== "create");

  console.log({ submitError });

  // const onFormSubmit = useCallback(
  //   async (values: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
  //     const formValues = tidyConnectionFormValues(values, connection.operations, workspaceId);

  //     setSubmitError(null);
  //     try {
  //       // This onSubmit comes from either ReplicationView.tsx (Connection Edit), or CreateConnectionContent.tsx (Connection Create).
  //       // TODO: onSubmit IoC
  //       const submitResult = await onSubmit?.(formValues);
  //       if (
  //         submitResult &&
  //         ((isSubmitCancel(submitResult) && !submitResult.submitCancel) || !isSubmitCancel(submitResult))
  //       ) {
  //         formikHelpers.resetForm({ values });
  //         // We need to clear the form changes otherwise the dirty form intercept service will prevent navigation
  //         clearFormChange(formId);
  //         onAfterSubmit?.(submitResult);
  //       }
  //     } catch (e) {
  //       setSubmitError(e);
  //     }
  //   },
  //   [connection.operations, workspaceId, onSubmit, clearFormChange, formId, onAfterSubmit]
  // );

  const frequencies = useFrequencyDropdownData(connection.scheduleData);

  return {
    initialValues,
    destDefinition,
    connection,
    mode,
    submitError,
    frequencies,
    formId,
    connectionDirty,
    isRefreshingCatalog,
    schemaHasBeenRefreshed,
    onAfterSubmit,
    setConnection,
    setSchemaHasBeenRefreshed,
    refreshConnectionCatalog,
    setSubmitError,
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

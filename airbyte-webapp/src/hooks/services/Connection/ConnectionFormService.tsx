import { FormikHelpers } from "formik";
import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Subject } from "rxjs";

import { DropDownRow } from "components";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionFormMode, ConnectionFormSubmitResult } from "views/Connection/ConnectionForm/ConnectionForm";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { useFormChangeTrackerService, useUniqueFormId } from "../FormChangeTracker";
import { ModalCancel } from "../Modal";

export interface ConnectionServiceProps {
  connection:
    | WebBackendConnectionRead
    | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);
  mode: ConnectionFormMode;
  onSubmit: (values: ConnectionFormValues) => Promise<ConnectionFormSubmitResult | void>;
  onAfterSubmit?: () => void;
  onFrequencySelect?: (item: DropDownRow.IDataItem) => void;
  onCancel?: () => void;
}

const useConnectionForm = ({
  connection,
  mode,
  onSubmit,
  onAfterSubmit,
  onFrequencySelect,
  onCancel,
}: ConnectionServiceProps) => {
  // Need to track form dirty state
  // Might be easy if form context is in here
  const [submitError, setSubmitError] = useState<Error | null>(null);
  const workspaceId = useCurrentWorkspaceId();
  const { clearFormChange } = useFormChangeTrackerService();
  const formId = useUniqueFormId();

  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const initialValues = useInitialValues(connection, destDefinition, mode !== "create");

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
        context: { isRequest: true },
      }) as unknown as ConnectionFormValues; // TODO: We should align these types

      formValues.operations = mapFormPropsToOperation(values, connection.operations, workspaceId);

      setSubmitError(null);
      try {
        await onSubmit(formValues);

        formikHelpers.resetForm({ values });
        clearFormChange(formId);

        onAfterSubmit?.();
      } catch (e) {
        if (!(e instanceof ModalCancel)) {
          setSubmitError(e);
        }
      }
    },
    [connection.operations, workspaceId, onSubmit, clearFormChange, formId, onAfterSubmit]
  );

  const errorMessage = useMemo(() => (submitError ? createFormErrorMessage(submitError) : null), [submitError]);
  const frequencies = useFrequencyDropdownData(connection.schedule);

  const formDirty = new Subject<boolean>();

  return {
    initialValues,
    destDefinition,
    connection,
    mode,
    errorMessage,
    frequencies,
    formId,
    formDirty,
    onFormSubmit,
    onAfterSubmit,
    onFrequencySelect,
    onCancel,
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

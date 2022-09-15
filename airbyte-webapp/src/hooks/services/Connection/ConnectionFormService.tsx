import { FormikHelpers } from "formik";
import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { useIntl } from "react-intl";

import { ConnectionScheduleType, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { useFormChangeTrackerService } from "../FormChangeTracker";
import { ModalCancel } from "../Modal";
import { ValuesProps } from "../useConnectionHook";

export type ConnectionOrPartialConnection =
  | WebBackendConnectionRead
  | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);

export interface ConnectionServiceProps {
  connection: ConnectionOrPartialConnection;
  mode: ConnectionFormMode;
  formId: string;
  onSubmit: (values: ValuesProps) => Promise<void>;
  onAfterSubmit?: () => void;
  onCancel?: () => void;
  formDirty: boolean;
}

const useConnectionForm = ({
  connection,
  mode,
  formId,
  onSubmit,
  onAfterSubmit,
  onCancel,
  formDirty,
}: ConnectionServiceProps) => {
  const [submitError, setSubmitError] = useState<Error | null>(null);
  const workspaceId = useCurrentWorkspaceId();
  const { clearFormChange } = useFormChangeTrackerService();
  const { formatMessage } = useIntl();

  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const initialValues = useInitialValues(connection, destDefinition, mode !== "create");

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      // Set the scheduleType based on the schedule value
      values["scheduleType"] = values.scheduleData?.basicSchedule
        ? ConnectionScheduleType.basic
        : ConnectionScheduleType.manual;

      // TODO: We should align these types
      // With the PATCH-style endpoint available we might be able to forego this pattern
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
        context: { isRequest: true },
      }) as unknown as ConnectionFormValues;

      formValues.operations = mapFormPropsToOperation(values, connection.operations, workspaceId);

      setSubmitError(null);
      try {
        // This onSubmit comes from either ReplicationView.tsx (Connection Edit), or CreateConnectionContent.tsx (Connection Create).
        await onSubmit(formValues);

        formikHelpers.resetForm({ values });
        // We need to clear the form changes otherwise the dirty form intercept service will prevent navigation
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

  const errorMessage = useMemo(
    () =>
      submitError
        ? generateMessageFromError(submitError)
        : formDirty
        ? formatMessage({ id: "connectionForm.validation.error" })
        : null,
    [formDirty, formatMessage, submitError]
  );
  const frequencies = useFrequencyDropdownData(connection.scheduleData);

  return {
    initialValues,
    destDefinition,
    connection,
    mode,
    errorMessage,
    frequencies,
    formId,
    onFormSubmit,
    onAfterSubmit,
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

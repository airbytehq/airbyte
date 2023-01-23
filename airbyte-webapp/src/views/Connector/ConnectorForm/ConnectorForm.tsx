import { Formik } from "formik";
import React, { ReactNode, useCallback } from "react";

import { FormChangeTracker } from "components/common/FormChangeTracker";

import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  SourceDefinitionSpecificationDraft,
} from "core/domain/connector";
import { FormikPatch } from "core/form/FormikPatch";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";

import { ConnectorFormContextProvider } from "./connectorFormContext";
import { FormRoot } from "./FormRoot";
import { ConnectorCardValues, ConnectorFormValues } from "./types";
import { useBuildForm } from "./useBuildForm";

export interface ConnectorFormProps {
  formType: "source" | "destination";
  formId?: string;
  /**
   * Definition of the connector might not be available if it's not released but only exists in frontend heap
   */
  selectedConnectorDefinition?: ConnectorDefinition;
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification | SourceDefinitionSpecificationDraft;
  onSubmit: (values: ConnectorFormValues) => Promise<void>;
  isEditMode?: boolean;
  formValues?: Partial<ConnectorFormValues>;
  connectionTestSuccess?: boolean;
  errorMessage?: React.ReactNode;
  connectorId?: string;
  footerClassName?: string;
  bodyClassName?: string;
  submitLabel?: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  full?: boolean;
  headerBlock?: ReactNode;
  footerComponent?: React.FC;
  renderFooter?: (formProps: {
    dirty: boolean;
    isSubmitting: boolean;
    isValid: boolean;
    resetConnectorForm: () => void;
    isEditMode?: boolean;
    formType: "source" | "destination";
    getValues: () => ConnectorFormValues;
  }) => ReactNode;
  renderWithCard?: boolean;
  /**
   * Called in case the user cancels the form - if not provided, no cancel button is rendered
   */
  onCancel?: () => void;
  /**
   * Called in case the user reset the form - if not provided, no reset button is rendered
   */
  onReset?: () => void;

  isTestConnectionInProgress?: boolean;
  onStopTesting?: () => void;
  testConnector?: (v?: ConnectorCardValues) => Promise<CheckConnectionRead>;
}

export const ConnectorForm: React.FC<ConnectorFormProps> = (props) => {
  const formId = useUniqueFormId(props.formId);
  const { clearFormChange } = useFormChangeTrackerService();

  const {
    formType,
    formValues,
    onSubmit,
    isEditMode,
    onStopTesting,
    testConnector,
    selectedConnectorDefinition,
    selectedConnectorDefinitionSpecification,
    connectorId,
    onReset,
  } = props;

  const { formFields, initialValues, validationSchema } = useBuildForm(
    Boolean(isEditMode),
    formType,
    selectedConnectorDefinitionSpecification,
    formValues
  );

  const castValues = useCallback(
    (values: ConnectorFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values: ConnectorFormValues) => {
      const valuesToSend = castValues(values);
      await onSubmit(valuesToSend);
      clearFormChange(formId);
    },
    [clearFormChange, formId, castValues, onSubmit]
  );

  return (
    <Formik
      validateOnBlur
      validateOnChange
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
      enableReinitialize
    >
      {({ dirty, resetForm }) => (
        <ConnectorFormContextProvider
          formType={formType}
          getValues={castValues}
          selectedConnectorDefinition={selectedConnectorDefinition}
          selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
          isEditMode={isEditMode}
          validationSchema={validationSchema}
          connectorId={connectorId}
        >
          <FormikPatch />
          <FormChangeTracker changed={dirty} formId={formId} />
          <FormRoot
            {...props}
            formFields={formFields}
            castValues={castValues}
            onReset={
              onReset &&
              (() => {
                onReset?.();
                resetForm();
              })
            }
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
          />
        </ConnectorFormContextProvider>
      )}
    </Formik>
  );
};

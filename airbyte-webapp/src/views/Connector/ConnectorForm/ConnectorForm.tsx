import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo } from "react";
import { useDeepCompareEffect } from "react-use";

import { FormChangeTracker } from "components/common/FormChangeTracker";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBaseItem, FormComponentOverrideProps } from "core/form/types";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { isDefined } from "utils/common";

import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorFormContextProvider, useConnectorForm } from "./connectorFormContext";
import { FormRoot } from "./FormRoot";
import { ConnectorCardValues, ConnectorFormValues } from "./types";
import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

/**
 * This function sets all initial const values in the form to current values
 * @param schema
 * @param initialValues
 * @constructor
 */
const PatchInitialValuesWithWidgetConfig: React.FC<{
  schema: JSONSchema7;
  initialValues: ConnectorFormValues;
}> = ({ schema, initialValues }) => {
  const { widgetsInfo } = useConnectorForm();
  const { setFieldValue } = useFormikContext<ConnectorFormValues>();

  useDeepCompareEffect(() => {
    const widgetsInfoEntries = Object.entries(widgetsInfo);

    // set all const fields to form field values, so we could send form
    const patchedConstValues = widgetsInfoEntries
      .filter(([_, value]) => isDefined(value.const))
      .reduce((acc, [key, value]) => setIn(acc, key, value.const), initialValues);

    // set default fields as current values, so values could be populated correctly
    // fix for https://github.com/airbytehq/airbyte/issues/6791
    const patchedDefaultValues = widgetsInfoEntries
      .filter(([key, value]) => isDefined(value.default) && !isDefined(getIn(patchedConstValues, key)))
      .reduce((acc, [key, value]) => setIn(acc, key, value.default), patchedConstValues);

    if (patchedDefaultValues?.connectionConfiguration) {
      setFieldValue("connectionConfiguration", patchedDefaultValues.connectionConfiguration);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [schema]);

  return null;
};

/**
 * Formik does not revalidate the form in case the validationSchema it's using changes.
 * This component just forces a revalidation of the form whenever the validation schema changes.
 */
const RevalidateOnValidationSchemaChange: React.FC<{ validationSchema: unknown }> = ({ validationSchema }) => {
  // The validationSchema is passed into this component instead of pulled from the FormikContext, since
  // due to https://github.com/jaredpalmer/formik/issues/2092 the validationSchema from the formik context will
  // always be undefined.
  const { validateForm } = useFormikContext();
  useEffect(() => {
    validateForm();
  }, [validateForm, validationSchema]);
  return null;
};

export interface ConnectorFormProps {
  formType: "source" | "destination";
  formId?: string;
  selectedConnectorDefinition?: ConnectorDefinition;
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  onSubmit: (values: ConnectorFormValues) => Promise<void> | void;
  isLoading?: boolean;
  isEditMode?: boolean;
  formValues?: Partial<ConnectorFormValues>;
  hasSuccess?: boolean;
  fetchingConnectorError?: Error | null;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;

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
    isLoading,
    isEditMode,
    isTestConnectionInProgress,
    onStopTesting,
    testConnector,
    selectedConnectorDefinition,
    selectedConnectorDefinitionSpecification,
    errorMessage,
  } = props;

  const specifications = useBuildInitialSchema(selectedConnectorDefinitionSpecification);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        ...(selectedConnectorDefinitionSpecification ? { name: { type: "string" } } : {}),
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name"],
    }),
    [isLoading, selectedConnectorDefinitionSpecification, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  // Overrides default field label(i.e "Source name", "Destination name")
  const uiOverrides = useMemo(() => {
    return {
      name: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorNameControl property={property} formType={formType} {...componentProps} />
        ),
      },
    };
  }, [formType]);

  const { uiWidgetsInfo, setUiWidgetsInfo, resetUiWidgetsInfo } = useBuildUiWidgetsContext(
    formFields,
    initialValues,
    uiOverrides
  );

  const validationSchema = useConstructValidationSchema(jsonSchema, uiWidgetsInfo);

  const getValues = useCallback(
    (values: ConnectorFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values: ConnectorFormValues) => {
      const valuesToSend = getValues(values);
      await onSubmit(valuesToSend);

      clearFormChange(formId);
    },
    [clearFormChange, formId, getValues, onSubmit]
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
      {({ dirty }) => (
        <ConnectorFormContextProvider
          formType={formType}
          widgetsInfo={uiWidgetsInfo}
          getValues={getValues}
          setUiWidgetsInfo={setUiWidgetsInfo}
          resetUiWidgetsInfo={resetUiWidgetsInfo}
          selectedConnectorDefinition={selectedConnectorDefinition}
          selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
          isEditMode={isEditMode}
          isLoadingSchema={isLoading}
          validationSchema={validationSchema}
        >
          <RevalidateOnValidationSchemaChange validationSchema={validationSchema} />
          <FormikPatch />
          <FormChangeTracker changed={dirty} formId={formId} />
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} initialValues={initialValues} />
          <FormRoot
            {...props}
            selectedConnector={selectedConnectorDefinitionSpecification}
            formFields={formFields}
            errorMessage={errorMessage}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
          />
        </ConnectorFormContextProvider>
      )}
    </Formik>
  );
};

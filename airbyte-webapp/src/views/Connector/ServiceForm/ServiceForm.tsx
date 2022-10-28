import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo } from "react";
import { useDeepCompareEffect } from "react-use";

import { FormChangeTracker } from "components/FormChangeTracker";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { isDestinationDefinitionSpecification } from "core/domain/connector/destination";
import { isSourceDefinition, isSourceDefinitionSpecification } from "core/domain/connector/source";
import { FormBaseItem, FormComponentOverrideProps } from "core/form/types";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { isDefined } from "utils/common";

import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { FormRoot } from "./FormRoot";
import { ServiceFormContextProvider, useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";
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
  initialValues: ServiceFormValues;
}> = ({ schema, initialValues }) => {
  const { widgetsInfo } = useServiceForm();
  const { setFieldValue } = useFormikContext<ServiceFormValues>();

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

/**
 * A component that will observe whenever the serviceType (selected connector)
 * changes and set the name of the connector to match the connector definition name.
 */
const SetDefaultName: React.FC = () => {
  const { setFieldValue } = useFormikContext();
  const { selectedService } = useServiceForm();

  useEffect(() => {
    if (!selectedService) {
      return;
    }

    const timeout = setTimeout(() => {
      // We need to push this out one execution slot, so the form isn't still in its
      // initialization status and won't react to this call but would just take the initialValues instead.
      setFieldValue("name", selectedService.name);
    });
    return () => clearTimeout(timeout);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedService]);

  return null;
};

export interface ServiceFormProps {
  formType: "source" | "destination";
  formId?: string;
  availableServices: ConnectorDefinition[];
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  onServiceSelect?: (id: string) => void;
  onSubmit: (values: ServiceFormValues) => Promise<void> | void;
  isLoading?: boolean;
  isEditMode?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  fetchingConnectorError?: Error | null;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;

  isTestConnectionInProgress?: boolean;
  onStopTesting?: () => void;
  testConnector?: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
}

export const ServiceForm: React.FC<ServiceFormProps> = (props) => {
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
    selectedConnectorDefinitionSpecification,
    availableServices,
    errorMessage,
  } = props;

  const specifications = useBuildInitialSchema(selectedConnectorDefinitionSpecification);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        serviceType: { type: "string" },
        ...(selectedConnectorDefinitionSpecification ? { name: { type: "string" } } : {}),
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name", "serviceType"],
    }),
    [isLoading, selectedConnectorDefinitionSpecification, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();

  useEffect(() => {
    if (!selectedConnectorDefinitionSpecification) {
      return;
    }

    const selectedServiceDefinition = availableServices.find((service) => {
      if (isSourceDefinition(service)) {
        const serviceDefinitionId = service.sourceDefinitionId;
        return (
          isSourceDefinitionSpecification(selectedConnectorDefinitionSpecification) &&
          serviceDefinitionId === selectedConnectorDefinitionSpecification.sourceDefinitionId
        );
      }
      const serviceDefinitionId = service.destinationDefinitionId;
      return (
        isDestinationDefinitionSpecification(selectedConnectorDefinitionSpecification) &&
        serviceDefinitionId === selectedConnectorDefinitionSpecification.destinationDefinitionId
      );
    });
    setDocumentationUrl(selectedServiceDefinition?.documentationUrl ?? "");
    setDocumentationPanelOpen(true);
  }, [availableServices, selectedConnectorDefinitionSpecification, setDocumentationPanelOpen, setDocumentationUrl]);

  const uiOverrides = useMemo(() => {
    return {
      name: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorNameControl property={property} formType={formType} {...componentProps} />
        ),
      },
      serviceType: {
        /* since we use <ConnectorServiceTypeControl/> outside formik form
           we need to keep the serviceType field in formik, but hide it.
           serviceType prop will be removed in further PR
        */
        component: () => null,
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
    (values: ServiceFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values: ServiceFormValues) => {
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
        <ServiceFormContextProvider
          widgetsInfo={uiWidgetsInfo}
          getValues={getValues}
          setUiWidgetsInfo={setUiWidgetsInfo}
          resetUiWidgetsInfo={resetUiWidgetsInfo}
          formType={formType}
          selectedConnector={selectedConnectorDefinitionSpecification}
          availableServices={availableServices}
          isEditMode={isEditMode}
          isLoadingSchema={isLoading}
          validationSchema={validationSchema}
        >
          {!isEditMode && <SetDefaultName />}
          <RevalidateOnValidationSchemaChange validationSchema={validationSchema} />
          <FormikPatch />
          <FormChangeTracker changed={dirty} formId={formId} />
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} initialValues={initialValues} />
          <FormRoot
            {...props}
            errorMessage={errorMessage}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
            formFields={formFields}
            selectedConnector={selectedConnectorDefinitionSpecification}
          />
        </ServiceFormContextProvider>
      )}
    </Formik>
  );
};

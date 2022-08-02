import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useDeepCompareEffect, useToggle } from "react-use";

import { FormChangeTracker } from "components/FormChangeTracker";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { isDestinationDefinitionSpecification } from "core/domain/connector/destination";
import { isSourceDefinition, isSourceDefinitionSpecification } from "core/domain/connector/source";
import { FormBaseItem, FormComponentOverrideProps } from "core/form/types";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { isDefined } from "utils/common";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";

import { CheckConnectionRead } from "../../../core/request/AirbyteClient";
import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorServiceTypeControl } from "./components/Controls/ConnectorServiceTypeControl";
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

/***
 * This function sets all initial const values in the form to current values
 * @param schema
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
  availableServices: ConnectorDefinition[];
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  onServiceSelect?: (id: string) => void;
  onSubmit: (values: ServiceFormValues) => void;
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

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

  const [isOpenRequestModal, toggleOpenRequestModal] = useToggle(false);
  const [initialRequestName, setInitialRequestName] = useState<string>();
  const {
    formType,
    formValues,
    onSubmit,
    isLoading,
    isTestConnectionInProgress,
    onStopTesting,
    testConnector,
    selectedConnectorDefinitionSpecification,
    availableServices,
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

  const uiOverrides = useMemo(
    () => ({
      name: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorNameControl property={property} formType={formType} {...componentProps} />
        ),
      },
      serviceType: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorServiceTypeControl
            property={property}
            formType={formType}
            onChangeServiceType={props.onServiceSelect}
            availableServices={props.availableServices}
            isEditMode={props.isEditMode}
            onOpenRequestConnectorModal={(name) => {
              setInitialRequestName(name);
              toggleOpenRequestModal();
            }}
            {...componentProps}
          />
        ),
      },
    }),
    [formType, props.onServiceSelect, props.availableServices, props.isEditMode, toggleOpenRequestModal]
  );

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgetsContext(formFields, initialValues, uiOverrides);

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
          formType={formType}
          selectedConnector={selectedConnectorDefinitionSpecification}
          availableServices={props.availableServices}
          isEditMode={props.isEditMode}
          isLoadingSchema={props.isLoading}
        >
          {!props.isEditMode && <SetDefaultName />}
          <FormikPatch />
          <FormChangeTracker changed={dirty} formId={formId} />
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} initialValues={initialValues} />
          <FormRoot
            {...props}
            errorMessage={props.errorMessage}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
            formFields={formFields}
          />
          {isOpenRequestModal && (
            <RequestConnectorModal
              connectorType={formType}
              initialName={initialRequestName}
              onClose={toggleOpenRequestModal}
            />
          )}
        </ServiceFormContextProvider>
      )}
    </Formik>
  );
};

export { ServiceForm };

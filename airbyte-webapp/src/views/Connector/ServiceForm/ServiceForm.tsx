import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToggle } from "react-use";

import { FormChangeTracker } from "components/FormChangeTracker";

import { ConnectorDefinition, ConnectorDefinitionSpecification, Scheduler } from "core/domain/connector";
import { FormBaseItem } from "core/form/types";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { isDefined } from "utils/common";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";

import { ConnectionConfiguration } from "../../../core/domain/connection";
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
}> = ({ schema }) => {
  const { widgetsInfo } = useServiceForm();
  const { values, resetForm } = useFormikContext<ServiceFormValues>();

  const valueRef = useRef<ConnectionConfiguration>();
  valueRef.current = values.connectionConfiguration;

  useEffect(() => {
    // set all const fields to form field values, so we could send form
    const constPatchedValues = Object.entries(widgetsInfo)
      .filter(([_, v]) => isDefined(v.const))
      .reduce((acc, [k, v]) => setIn(acc, k, v.const), valueRef.current);

    // set default fields as current values, so values could be populated correctly
    // fix for https://github.com/airbytehq/airbyte/issues/6791
    const defaultPatchedValues = Object.entries(widgetsInfo)
      .filter(([k, v]) => isDefined(v.default) && !isDefined(getIn(constPatchedValues, k)))
      .reduce((acc, [k, v]) => setIn(acc, k, v.default), constPatchedValues);

    resetForm({
      values: {
        ...values,
        connectionConfiguration: defaultPatchedValues,
      },
    });

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
    if (selectedService) {
      setFieldValue("name", selectedService.name);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedService]);

  return null;
};

export type ServiceFormProps = {
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
  testConnector?: (v?: ServiceFormValues) => Promise<Scheduler>;
};

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

  const uiOverrides = useMemo(
    () => ({
      name: {
        component: (property: FormBaseItem) => <ConnectorNameControl property={property} formType={formType} />,
      },
      serviceType: {
        component: (property: FormBaseItem) => (
          <ConnectorServiceTypeControl
            property={property}
            formType={formType}
            documentationUrl={selectedConnectorDefinitionSpecification?.documentationUrl}
            onChangeServiceType={props.onServiceSelect}
            availableServices={props.availableServices}
            isEditMode={props.isEditMode}
            onOpenRequestConnectorModal={(name) => {
              setInitialRequestName(name);
              toggleOpenRequestModal();
            }}
          />
        ),
      },
    }),
    [
      formType,
      selectedConnectorDefinitionSpecification?.documentationUrl,
      props.onServiceSelect,
      props.availableServices,
      props.isEditMode,
      toggleOpenRequestModal,
    ]
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
      validateOnBlur={true}
      validateOnChange={true}
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
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
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} />
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

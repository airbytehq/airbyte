import React, { useCallback, useEffect, useMemo } from "react";
import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import { useToggle } from "react-use";

import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";
import { ServiceFormValues } from "./types";
import {
  ServiceFormContextProvider,
  useServiceForm,
} from "./serviceFormContext";
import { FormRoot } from "./FormRoot";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";
import { FormBaseItem } from "core/form/types";
import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorServiceTypeControl } from "./components/Controls/ConnectorServiceTypeControl";
import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  Scheduler,
} from "core/domain/connector";
import { isDefined } from "utils/common";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { useCheckConnector } from "hooks/services/useConnector";

export type ServiceFormProps = {
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  selectedConnector?: ConnectorDefinitionSpecification;
  onServiceSelect?: (id: string) => void;
  onSubmit: (values: ServiceFormValues) => void;
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  fetchingConnectorError?: Error | null;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
};

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

/***
 * This function sets all initial const values in the form to current values
 * @param schema
 * @constructor
 */
const PatchInitialValuesWithWidgetConfig: React.FC<{ schema: JSONSchema7 }> = ({
  schema,
}) => {
  const { widgetsInfo } = useServiceForm();
  const { values, setValues } = useFormikContext();

  useEffect(() => {
    // set all const fields to form field values, so we could send form
    const constPatchedValues = Object.entries(widgetsInfo)
      .filter(([_, v]) => isDefined(v.const))
      .reduce((acc, [k, v]) => setIn(acc, k, v.const), values);

    // set default fields as current values, so values could be populated correctly
    // fix for https://github.com/airbytehq/airbyte/issues/6791
    const defaultPatchedValues = Object.entries(widgetsInfo)
      .filter(
        ([k, v]) =>
          isDefined(v.default) && !isDefined(getIn(constPatchedValues, k))
      )
      .reduce((acc, [k, v]) => setIn(acc, k, v.default), constPatchedValues);

    setValues(defaultPatchedValues);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [schema]);

  return null;
};

const useTestConnector = (
  props: ServiceFormProps
): {
  loading: boolean;
  isSuccess: boolean;
  error: any;
  f: (v?: ServiceFormValues) => Promise<Scheduler>;
} => {
  const { mutateAsync, isLoading, error, isSuccess } = useCheckConnector(
    props.formType
  );

  const controller = new AbortController();
  const signal = controller.signal;

  return {
    loading: isLoading,
    isSuccess,
    error: error,
    f: async (values) => {
      if (values) {
        const selectedConnectorDefinitionId: any = props.selectedConnector
          ? ConnectorSpecification.id(props.selectedConnector)
          : undefined;

        const fun = mutateAsync({
          connectionConfiguration: values.connectionConfiguration,
          selectedConnectorDefinitionId,
        });

        return fun;
      } else {
        return mutateAsync({
          selectedConnectorId: "e2152054-cb99-41b8-ae81-f5f45363bb12",
        });
      }
    },
  };
};

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const [isOpenRequestModal, toggleOpenRequestModal] = useToggle(false);
  const {
    formType,
    formValues,
    onSubmit,
    isLoading,
    selectedConnector,
  } = props;

  const {
    f: testConnector,
    error,
    loading: isTestConnectionInProgress,
  } = useTestConnector(props);

  const specifications = useBuildInitialSchema(selectedConnector);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        name: { type: "string" },
        serviceType: { type: "string" },
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name", "serviceType"],
    }),
    [isLoading, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  const uiOverrides = useMemo(
    () => ({
      name: {
        component: (property: FormBaseItem) => (
          <ConnectorNameControl property={property} formType={formType} />
        ),
      },
      serviceType: {
        component: (property: FormBaseItem) => (
          <ConnectorServiceTypeControl
            property={property}
            formType={formType}
            documentationUrl={selectedConnector?.documentationUrl}
            onChangeServiceType={props.onServiceSelect}
            availableServices={props.availableServices}
            allowChangeConnector={props.allowChangeConnector}
            isEditMode={props.isEditMode}
            onOpenRequestConnectorModal={toggleOpenRequestModal}
          />
        ),
      },
    }),
    [
      formType,
      selectedConnector?.documentationUrl,
      props.onServiceSelect,
      props.availableServices,
      props.allowChangeConnector,
      props.isEditMode,
      toggleOpenRequestModal,
    ]
  );

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgetsContext(
    formFields,
    initialValues,
    uiOverrides
  );

  const validationSchema = useConstructValidationSchema(
    jsonSchema,
    uiWidgetsInfo
  );

  const getValues = useCallback(
    (values: ServiceFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values) => {
      const valuesToSend = getValues(values);

      await testConnector(valuesToSend);

      return onSubmit(valuesToSend);
    },
    [getValues, testConnector, onSubmit]
  );

  return (
    <Formik
      validateOnBlur={true}
      validateOnChange={true}
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
    >
      {({ setSubmitting }) => (
        <ServiceFormContextProvider
          widgetsInfo={uiWidgetsInfo}
          getValues={getValues}
          setUiWidgetsInfo={setUiWidgetsInfo}
          formType={formType}
          selectedConnector={selectedConnector}
          availableServices={props.availableServices}
          isEditMode={props.isEditMode}
          isLoadingSchema={props.isLoading}
        >
          <FormikPatch />
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} />
          <FormRoot
            {...props}
            errorMessage={
              props.errorMessage || (error && createFormErrorMessage(error))
            }
            isTestConnectionInProgress={isTestConnectionInProgress}
            onRetest={async () => {
              setSubmitting(true);
              await testConnector();
              setSubmitting(false);
            }}
            formFields={formFields}
          />
          {isOpenRequestModal && (
            <RequestConnectorModal
              connectorType={formType}
              onClose={toggleOpenRequestModal}
            />
          )}
        </ServiceFormContextProvider>
      )}
    </Formik>
  );
};
export default ServiceForm;

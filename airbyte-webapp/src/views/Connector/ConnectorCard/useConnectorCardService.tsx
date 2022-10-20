import { JSONSchema7 } from "json-schema";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AnySchema } from "yup";

import { Connector, ConnectorSpecification } from "core/domain/connector";
import { CheckConnectionRead, SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import {
  FormBaseItem,
  FormBlock,
  FormComponentOverrideProps,
  WidgetConfig,
  WidgetConfigMap,
} from "../../../core/form/types";
import { useFormChangeTrackerService, useUniqueFormId } from "../../../hooks/services/FormChangeTracker";
import { ConnectorNameControl } from "../ServiceForm/components/Controls/ConnectorNameControl";
import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
} from "../ServiceForm/useBuildForm";
import { ConnectorCardProps } from "./interfaces";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

interface UseConnectorCardServiceHookResult {
  advancedMode: boolean;
  isFormSubmitting: boolean;
  isTestConnectionInProgress: boolean;
  job?: SynchronousJobRead | null;
  onHandleSubmit: (values: ServiceFormValues) => Promise<void>;
  onStopTesting: () => void;
  saved: boolean;
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
  error: Error | null;
  selectedConnectorDefinitionSpecificationId?: string;
  uniqueFormId?: string;
  jsonSchema: JSONSchema7;
  initialValues: ServiceFormValues;
  formFields: FormBlock;
  validationSchema: AnySchema;
  uiWidgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  resetUiWidgetsInfo: () => void;
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
  onFormSubmit: (values: ServiceFormValues) => Promise<void>;
}

export const useConnectorCardService = (props: ConnectorCardProps): UseConnectorCardServiceHookResult => {
  const {
    selectedConnectorDefinitionSpecification,
    isLoading,
    formType,
    availableServices,
    formValues,
    onSubmit,
    jobInfo,
    formId,
  } = props;
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [advancedMode] = useAdvancedModeSetting();

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);
  const { trackTestConnectorFailure, trackTestConnectorSuccess, trackTestConnectorStarted } =
    useAnalyticsTrackFunctions(formType);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [selectedConnectorDefinitionSpecification, reset]);

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);
    setIsFormSubmitting(true);

    const connector = availableServices.find((item) => Connector.id(item) === values.serviceType);

    const testConnectorWithTracking = async () => {
      trackTestConnectorStarted(connector);
      try {
        await testConnector(values);
        trackTestConnectorSuccess(connector);
      } catch (e) {
        trackTestConnectorFailure(connector);
        throw e;
      }
    };

    try {
      await testConnectorWithTracking();
      onSubmit(values);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

  const uniqueFormId = useUniqueFormId(formId);
  const { clearFormChange } = useFormChangeTrackerService();

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

      clearFormChange(uniqueFormId);
    },
    [clearFormChange, uniqueFormId, getValues, onSubmit]
  );

  return {
    advancedMode,
    error,
    formFields,
    getValues,
    initialValues,
    isFormSubmitting,
    isTestConnectionInProgress,
    job,
    jsonSchema,
    onFormSubmit,
    onHandleSubmit,
    onStopTesting,
    resetUiWidgetsInfo,
    saved,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    testConnector,
    uiWidgetsInfo,
    uniqueFormId,
    validationSchema,
  };
};

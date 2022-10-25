import { JSONSchema7 } from "json-schema";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AnySchema } from "yup";

import { ConnectorSpecification } from "core/domain/connector";
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
import { useTestConnector } from "./useTestConnector";

interface UseConnectorCardServiceHookResult {
  advancedMode: boolean;
  error: Error | null;
  formFields: FormBlock;
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
  initialValues: ServiceFormValues;
  isFormSubmitting: boolean;
  isTestConnectionInProgress: boolean;
  job?: SynchronousJobRead | null;
  jsonSchema: JSONSchema7;
  onFormSubmit: (values: ServiceFormValues) => Promise<void>;
  onStopTesting: () => void;
  resetUiWidgetsInfo: () => void;
  selectedConnectorDefinitionSpecificationId?: string;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
  uiWidgetsInfo: WidgetConfigMap;
  uniqueFormId?: string;
  validationSchema: AnySchema;
}

export const useConnectorCardService = (props: ConnectorCardProps): UseConnectorCardServiceHookResult => {
  const { selectedConnectorDefinitionSpecification, isLoading, formType, formValues, onSubmit, jobInfo, formId } =
    props;
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const [isFormSubmitting] = useState(false);
  const [advancedMode] = useAdvancedModeSetting();

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [selectedConnectorDefinitionSpecification, reset]);

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
    onStopTesting,
    resetUiWidgetsInfo,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    testConnector,
    uiWidgetsInfo,
    uniqueFormId,
    validationSchema,
  };
};

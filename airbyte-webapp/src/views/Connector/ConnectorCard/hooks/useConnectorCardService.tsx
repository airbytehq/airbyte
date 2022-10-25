import { JSONSchema7 } from "json-schema";
import { useCallback, useEffect, useState } from "react";
import { AnySchema } from "yup";

import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import { FormBlock, WidgetConfig, WidgetConfigMap } from "../../../../core/form/types";
import { useFormChangeTrackerService, useUniqueFormId } from "../../../../hooks/services/FormChangeTracker";
import { ConnectorCardProps } from "../interfaces";
import { useTestConnector } from "../useTestConnector";
import { useOnHandeSubmit } from "./useOnHandleSubmit";
import { useUIWidget } from "./useUIWidget";

interface UseConnectorCardServiceHookResult {
  formFields: FormBlock;
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
  initialValues: ServiceFormValues;
  isFormSubmitting: boolean;
  job?: SynchronousJobRead | null;
  jsonSchema: JSONSchema7;
  onFormSubmit: (values: ServiceFormValues) => Promise<void>;
  resetUiWidgetsInfo: () => void;
  saved: boolean;
  selectedConnectorDefinitionSpecificationId?: string;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  uiWidgetsInfo: WidgetConfigMap;
  uniqueFormId?: string;
  validationSchema: AnySchema;
}

export const useConnectorCardService = (props: ConnectorCardProps): UseConnectorCardServiceHookResult => {
  const { selectedConnectorDefinitionSpecification, formType, availableServices, onSubmit, jobInfo, formId } = props;
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const { testConnector, reset } = useTestConnector(props);
  const { isFormSubmitting, saved, onHandleSubmit } = useOnHandeSubmit({
    setErrorStatusRequest,
    availableServices,
    formType,
    testConnector,
    onSubmit,
  });
  const {
    formFields,
    getValues,
    initialValues,
    jsonSchema,
    resetUiWidgetsInfo,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    uiWidgetsInfo,
    validationSchema,
  } = useUIWidget(props);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [selectedConnectorDefinitionSpecification, reset]);

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);
  const uniqueFormId = useUniqueFormId(formId);
  const { clearFormChange } = useFormChangeTrackerService();

  const onFormSubmit = useCallback(
    async (values: ServiceFormValues) => {
      const valuesToSend = getValues(values);
      await onHandleSubmit(valuesToSend);

      clearFormChange(uniqueFormId);
    },
    [clearFormChange, uniqueFormId, getValues, onHandleSubmit]
  );

  return {
    formFields,
    getValues,
    initialValues,
    isFormSubmitting,
    job,
    jsonSchema,
    onFormSubmit,
    resetUiWidgetsInfo,
    saved,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    uiWidgetsInfo,
    uniqueFormId,
    validationSchema,
  };
};

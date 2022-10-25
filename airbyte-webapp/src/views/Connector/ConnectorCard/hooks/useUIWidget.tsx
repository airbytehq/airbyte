import { JSONSchema7 } from "json-schema";
import { useCallback, useMemo } from "react";
import { AnySchema } from "yup";

import { ConnectorSpecification } from "core/domain/connector";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import {
  FormBaseItem,
  FormBlock,
  FormComponentOverrideProps,
  WidgetConfig,
  WidgetConfigMap,
} from "../../../../core/form/types";
import { ConnectorNameControl } from "../../ServiceForm/components/Controls/ConnectorNameControl";
import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
} from "../../ServiceForm/useBuildForm";
import { ConnectorCardProps } from "../interfaces";

interface UseUIWidgetHookResult {
  formFields: FormBlock;
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
  initialValues: ServiceFormValues;
  jsonSchema: JSONSchema7;
  resetUiWidgetsInfo: () => void;
  selectedConnectorDefinitionSpecificationId?: string;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  uiWidgetsInfo: WidgetConfigMap;
  validationSchema: AnySchema;
}

export const useUIWidget = (props: ConnectorCardProps): UseUIWidgetHookResult => {
  const { selectedConnectorDefinitionSpecification, isLoading, formType, formValues } = props;

  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

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

  return {
    formFields,
    getValues,
    initialValues,
    jsonSchema,
    resetUiWidgetsInfo,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    uiWidgetsInfo,
    validationSchema,
  };
};

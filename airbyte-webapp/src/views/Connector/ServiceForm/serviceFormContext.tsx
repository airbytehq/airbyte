import { getIn, useFormikContext } from "formik";
import React, { useContext, useMemo } from "react";
import { AnySchema } from "yup";

import { Connector, ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { WidgetConfigMap } from "core/form/types";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { ServiceFormValues } from "./types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "./utils";

interface ServiceFormContext {
  formType: "source" | "destination";
  getValues: (values: ServiceFormValues) => ServiceFormValues;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  unfinishedFlows: Record<string, { startValue: string; id: number | string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  resetServiceForm: () => void;
  selectedService?: ConnectorDefinition;
  selectedConnector?: ConnectorDefinitionSpecification;
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  isAuthFlowSelected?: boolean;
  authFieldsToHide: string[];
  validationSchema: AnySchema;
  authErrors: Record<string, string>;
}

const serviceFormContext = React.createContext<ServiceFormContext | null>(null);

export const useServiceForm = (): ServiceFormContext => {
  const serviceFormHelpers = useContext(serviceFormContext);
  if (!serviceFormHelpers) {
    throw new Error("useServiceForm should be used within ServiceFormContextProvider");
  }
  return serviceFormHelpers;
};

interface ServiceFormContextProviderProps {
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  resetUiWidgetsInfo: () => void;
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  availableServices: ConnectorDefinition[];
  getValues: (values: ServiceFormValues) => ServiceFormValues;
  selectedConnector?: ConnectorDefinitionSpecification;
  validationSchema: AnySchema;
}

export const ServiceFormContextProvider: React.FC<ServiceFormContextProviderProps> = ({
  availableServices,
  children,
  widgetsInfo,
  setUiWidgetsInfo,
  resetUiWidgetsInfo,
  selectedConnector,
  getValues,
  formType,
  isLoadingSchema,
  validationSchema,
  isEditMode,
}) => {
  const { values, resetForm, getFieldMeta, submitCount } = useFormikContext<ServiceFormValues>();

  const allowOAuthConnector = useFeature(FeatureItem.AllowOAuthConnector);

  const { serviceType } = values;
  const selectedService = useMemo(
    () => availableServices.find((s) => Connector.id(s) === serviceType),
    [availableServices, serviceType]
  );

  const isAuthFlowSelected = useMemo(
    () =>
      allowOAuthConnector &&
      selectedConnector?.advancedAuth &&
      selectedConnector?.advancedAuth.predicateValue ===
        getIn(getValues(values), makeConnectionConfigurationPath(selectedConnector?.advancedAuth.predicateKey ?? [])),
    [selectedConnector, allowOAuthConnector, values, getValues]
  );

  const authFieldsToHide = useMemo(
    () =>
      isAuthFlowSelected
        ? Object.values(serverProvidedOauthPaths(selectedConnector)).map((f) =>
            makeConnectionConfigurationPath(f.path_in_connector_config)
          )
        : [],
    [selectedConnector, isAuthFlowSelected]
  );

  const authErrors = useMemo(() => {
    // key of field path, value of error code
    return authFieldsToHide.reduce<Record<string, string>>((authErrors, fieldName) => {
      const { error } = getFieldMeta(fieldName);
      if (submitCount > 0 && error) {
        authErrors[fieldName] = error;
      }
      return authErrors;
    }, {});
  }, [authFieldsToHide, getFieldMeta, submitCount]);
  const ctx = useMemo<ServiceFormContext>(() => {
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      authErrors,
      widgetsInfo,
      isAuthFlowSelected,
      authFieldsToHide,
      getValues,
      setUiWidgetsInfo,
      selectedService,
      selectedConnector,
      formType,
      isLoadingSchema,
      validationSchema,
      isEditMode,
      unfinishedFlows,
      addUnfinishedFlow: (path, info) =>
        setUiWidgetsInfo("_common.unfinishedFlows", {
          ...unfinishedFlows,
          [path]: info ?? {},
        }),
      removeUnfinishedFlow: (path: string) =>
        setUiWidgetsInfo(
          "_common.unfinishedFlows",
          Object.fromEntries(Object.entries(unfinishedFlows).filter(([key]) => key !== path))
        ),
      resetServiceForm: () => {
        resetForm();
        resetUiWidgetsInfo();
      },
    };
  }, [
    authErrors,
    widgetsInfo,
    isAuthFlowSelected,
    authFieldsToHide,
    getValues,
    setUiWidgetsInfo,
    selectedService,
    selectedConnector,
    formType,
    isLoadingSchema,
    validationSchema,
    isEditMode,
    resetForm,
    resetUiWidgetsInfo,
  ]);

  return <serviceFormContext.Provider value={ctx}>{children}</serviceFormContext.Provider>;
};

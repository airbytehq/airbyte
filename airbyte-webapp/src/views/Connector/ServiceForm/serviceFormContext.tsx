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
  hasAuthError: boolean;
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

  const hasAuthError = useMemo(() => {
    //todo: we may want to return the entire error message, then in the component check if it is `form.empty.error`
    //key of fieldname, value of error code

    // we calculate by this rather than traversing the error object to look for auth errors
    // because doing so would be difficult to match the correct error to the correct field due to differences in
    // spec structure

    return (
      authFieldsToHide.filter((fieldString) => {
        const meta = getFieldMeta(fieldString);
        return submitCount > 0 && meta.error;
      }).length > 0
    );
  }, [authFieldsToHide, getFieldMeta, submitCount]);
  const ctx = useMemo<ServiceFormContext>(() => {
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      hasAuthError,
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
    hasAuthError,
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

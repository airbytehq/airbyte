import { getIn, useFormikContext } from "formik";
import React, { useContext, useMemo } from "react";

import { Connector, ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { WidgetConfigMap } from "core/form/types";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";

import { ServiceFormValues } from "./types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "./utils";

type Context = {
  formType: "source" | "destination";
  getValues: (values: ServiceFormValues) => ServiceFormValues;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  unfinishedFlows: Record<string, { startValue: string; id: number | string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  resetUiFormProgress: () => void;
  selectedService?: ConnectorDefinition;
  selectedConnector?: ConnectorDefinitionSpecification;
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  isAuthFlowSelected?: boolean;
  authFieldsToHide: string[];
};

const FormWidgetContext = React.createContext<Context | null>(null);

const useServiceForm = (): Context => {
  const serviceFormHelpers = useContext(FormWidgetContext);
  if (!serviceFormHelpers) {
    throw new Error("useServiceForm should be used within ServiceFormContextProvider");
  }
  return serviceFormHelpers;
};

const ServiceFormContextProvider: React.FC<{
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  availableServices: ConnectorDefinition[];
  getValues: (values: ServiceFormValues) => ServiceFormValues;
  selectedConnector?: ConnectorDefinitionSpecification;
}> = ({
  availableServices,
  children,
  widgetsInfo,
  setUiWidgetsInfo,
  selectedConnector,
  getValues,
  formType,
  isLoadingSchema,
  isEditMode,
}) => {
  const { values } = useFormikContext<ServiceFormValues>();
  const { hasFeature } = useFeatureService();

  const serviceType = values.serviceType;
  const selectedService = useMemo(
    () => availableServices.find((s) => Connector.id(s) === serviceType),
    [availableServices, serviceType]
  );

  const isAuthFlowSelected = useMemo(
    () =>
      hasFeature(FeatureItem.AllowOAuthConnector) &&
      selectedConnector?.advancedAuth &&
      selectedConnector?.advancedAuth.predicateValue ===
        getIn(getValues(values), makeConnectionConfigurationPath(selectedConnector?.advancedAuth.predicateKey)),
    [selectedConnector, hasFeature, values, getValues]
  );

  const authFieldsToHide = useMemo(
    () =>
      Object.values(serverProvidedOauthPaths(selectedConnector)).map((f) =>
        makeConnectionConfigurationPath(f.path_in_connector_config)
      ),
    [selectedConnector]
  );

  const ctx = useMemo<Context>(() => {
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      widgetsInfo,
      isAuthFlowSelected,
      authFieldsToHide: isAuthFlowSelected ? authFieldsToHide : [],
      getValues,
      setUiWidgetsInfo,
      selectedService,
      selectedConnector,
      formType,
      isLoadingSchema,
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
      resetUiFormProgress: () => setUiWidgetsInfo("_common.unfinishedFlows", {}),
    };
  }, [
    widgetsInfo,
    isAuthFlowSelected,
    authFieldsToHide,
    getValues,
    setUiWidgetsInfo,
    selectedService,
    selectedConnector,
    formType,
    isLoadingSchema,
    isEditMode,
  ]);

  return <FormWidgetContext.Provider value={ctx}>{children}</FormWidgetContext.Provider>;
};

export { useServiceForm, ServiceFormContextProvider };

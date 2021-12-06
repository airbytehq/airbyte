import React, { useContext, useMemo } from "react";
import { getIn, useFormikContext } from "formik";

import { WidgetConfigMap } from "core/form/types";
import {
  Connector,
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
} from "core/domain/connector";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import {
  makeConnectionConfigurationPath,
  serverProvidedOauthPaths,
} from "./utils";

type Context = {
  formType: "source" | "destination";
  selectedService?: ConnectorDefinition;
  selectedConnector?: ConnectorDefinitionSpecification;
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  isAuthFlowSelected?: boolean;
  isRequestConnectorModalOpen: boolean;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  unfinishedFlows: Record<string, { startValue: string; id: number | string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  resetUiFormProgress: () => void;
  authFieldsToHide: string[];
};

const context: Context = {
  formType: "source",
  isRequestConnectorModalOpen: false,
  widgetsInfo: {},
  authFieldsToHide: [],
  setUiWidgetsInfo: (_path: string, _value: Record<string, unknown>) => ({}),
  unfinishedFlows: {},
  addUnfinishedFlow: (_key: string, _info?: Record<string, unknown>) => ({}),
  removeUnfinishedFlow: (_key: string) => ({}),
  resetUiFormProgress: () => ({}),
};

const FormWidgetContext = React.createContext<Context>(context);

const useServiceForm = (): Context => useContext(FormWidgetContext);

const ServiceFormContextProvider: React.FC<{
  widgetsInfo: WidgetConfigMap;
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  serviceType?: string;
  availableServices: ConnectorDefinition[];
  selectedConnector?: ConnectorDefinitionSpecification;
  isEditMode?: boolean;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
}> = ({
  availableServices,
  serviceType,
  children,
  widgetsInfo,
  setUiWidgetsInfo,
  selectedConnector,
  ...props
}) => {
  const selectedService = availableServices.find(
    (s) => Connector.id(s) === serviceType
  );
  const { values } = useFormikContext();

  const { hasFeature } = useFeatureService();
  const isAuthFlowSelected =
    hasFeature(FeatureItem.AllowOAuthConnector) &&
    selectedConnector?.advancedAuth &&
    selectedConnector?.advancedAuth.predicateValue ===
      getIn(
        values,
        makeConnectionConfigurationPath(
          selectedConnector?.advancedAuth.predicateKey
        )
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
      setUiWidgetsInfo,
      selectedService,
      selectedConnector,
      formType: props.formType,
      isLoadingSchema: props.isLoadingSchema,
      isEditMode: props.isEditMode,
      unfinishedFlows: unfinishedFlows,
      isRequestConnectorModalOpen: false,
      addUnfinishedFlow: (path, info) =>
        setUiWidgetsInfo("_common.unfinishedFlows", {
          ...unfinishedFlows,
          [path]: info ?? {},
        }),
      removeUnfinishedFlow: (path: string) =>
        setUiWidgetsInfo(
          "_common.unfinishedFlows",
          Object.fromEntries(
            Object.entries(unfinishedFlows).filter(([key]) => key !== path)
          )
        ),
      resetUiFormProgress: () => {
        setUiWidgetsInfo("_common.unfinishedFlows", {});
      },
    };
  }, [
    props,
    widgetsInfo,
    selectedConnector,
    isAuthFlowSelected,
    authFieldsToHide,
    selectedService,
    setUiWidgetsInfo,
  ]);

  return (
    <FormWidgetContext.Provider value={ctx}>
      {children}
    </FormWidgetContext.Provider>
  );
};

export { useServiceForm, ServiceFormContextProvider };

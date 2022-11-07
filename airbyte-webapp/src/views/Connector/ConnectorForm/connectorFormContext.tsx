import { useFormikContext } from "formik";
import React, { useContext, useMemo } from "react";
import { AnySchema } from "yup";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { WidgetConfigMap } from "core/form/types";

import { ConnectorFormValues } from "./types";

interface ConnectorFormContext {
  formType: "source" | "destination";
  getValues: <T = unknown>(values: ConnectorFormValues<T>) => ConnectorFormValues<T>;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  unfinishedFlows: Record<string, { startValue: string; id: number | string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  resetConnectorForm: () => void;
  selectedService?: ConnectorDefinition;
  selectedConnector?: ConnectorDefinitionSpecification;
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  validationSchema: AnySchema;
}

const connectorFormContext = React.createContext<ConnectorFormContext | null>(null);

export const useConnectorForm = (): ConnectorFormContext => {
  const connectorFormHelpers = useContext(connectorFormContext);
  if (!connectorFormHelpers) {
    throw new Error("useConnectorForm should be used within ConnectorFormContextProvider");
  }
  return connectorFormHelpers;
};

interface ConnectorFormContextProviderProps {
  selectedConnectorDefinition?: ConnectorDefinition;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  resetUiWidgetsInfo: () => void;
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  getValues: <T = unknown>(values: ConnectorFormValues<T>) => ConnectorFormValues<T>;
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  validationSchema: AnySchema;
}

export const ConnectorFormContextProvider: React.FC<React.PropsWithChildren<ConnectorFormContextProviderProps>> = ({
  selectedConnectorDefinition,
  children,
  widgetsInfo,
  setUiWidgetsInfo,
  resetUiWidgetsInfo,
  selectedConnectorDefinitionSpecification,
  getValues,
  formType,
  isLoadingSchema,
  validationSchema,
  isEditMode,
}) => {
  const { resetForm } = useFormikContext<ConnectorFormValues>();

  const ctx = useMemo<ConnectorFormContext>(() => {
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      widgetsInfo,
      getValues,
      setUiWidgetsInfo,
      selectedConnectorDefinition,
      selectedConnectorDefinitionSpecification,
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
      resetConnectorForm: () => {
        resetForm();
        resetUiWidgetsInfo();
      },
    };
  }, [
    widgetsInfo,
    getValues,
    setUiWidgetsInfo,
    selectedConnectorDefinition,
    selectedConnectorDefinitionSpecification,
    formType,
    isLoadingSchema,
    validationSchema,
    isEditMode,
    resetForm,
    resetUiWidgetsInfo,
  ]);

  return <connectorFormContext.Provider value={ctx}>{children}</connectorFormContext.Provider>;
};

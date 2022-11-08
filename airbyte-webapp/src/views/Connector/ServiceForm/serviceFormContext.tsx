import { useFormikContext } from "formik";
import React, { useContext, useMemo } from "react";
import { AnySchema } from "yup";

import { Connector, ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { WidgetConfigMap } from "core/form/types";

import { ServiceFormValues } from "./types";

interface ServiceFormContext {
  formType: "source" | "destination";
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
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
  validationSchema: AnySchema;
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
  getValues: <T = unknown>(values: ServiceFormValues<T>) => ServiceFormValues<T>;
  selectedConnector?: ConnectorDefinitionSpecification;
  validationSchema: AnySchema;
}

export const ServiceFormContextProvider: React.FC<React.PropsWithChildren<ServiceFormContextProviderProps>> = ({
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
  const { values, resetForm } = useFormikContext<ServiceFormValues>();

  const { serviceType } = values;
  const selectedService = useMemo(
    () => availableServices.find((s) => Connector.id(s) === serviceType),
    [availableServices, serviceType]
  );

  const ctx = useMemo<ServiceFormContext>(() => {
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      widgetsInfo,
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
    widgetsInfo,
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

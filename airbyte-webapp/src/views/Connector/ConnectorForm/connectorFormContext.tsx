import React, { useContext, useMemo } from "react";
import { useFormContext } from "react-hook-form";
import { AnySchema } from "yup";

import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  SourceDefinitionSpecificationDraft,
} from "core/domain/connector";

import { ConnectorFormValues } from "./types";

interface ConnectorFormContext {
  formType: "source" | "destination";
  getValues: <T = unknown>(values: ConnectorFormValues<T>) => ConnectorFormValues<T>;
  resetConnectorForm: () => void;
  selectedConnectorDefinition?: ConnectorDefinition;
  selectedConnectorDefinitionSpecification: ConnectorDefinitionSpecification | SourceDefinitionSpecificationDraft;
  isEditMode?: boolean;
  validationSchema: AnySchema;
  connectorId?: string;
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
  formType: "source" | "destination";
  isEditMode?: boolean;
  getValues: <T = unknown>(values: ConnectorFormValues<T>) => ConnectorFormValues<T>;
  selectedConnectorDefinitionSpecification: ConnectorDefinitionSpecification | SourceDefinitionSpecificationDraft;
  validationSchema: AnySchema;
  connectorId?: string;
}

export const ConnectorFormContextProvider: React.FC<React.PropsWithChildren<ConnectorFormContextProviderProps>> = ({
  selectedConnectorDefinition,
  children,
  selectedConnectorDefinitionSpecification,
  getValues,
  formType,
  validationSchema,
  isEditMode,
  connectorId,
}) => {
  const { reset } = useFormContext();

  const ctx = useMemo<ConnectorFormContext>(() => {
    const context: ConnectorFormContext = {
      getValues,
      selectedConnectorDefinition,
      selectedConnectorDefinitionSpecification,
      formType,
      validationSchema,
      isEditMode,
      connectorId,
      resetConnectorForm: () => {
        reset();
      },
    };
    return context;
  }, [
    getValues,
    selectedConnectorDefinition,
    selectedConnectorDefinitionSpecification,
    formType,
    validationSchema,
    isEditMode,
    connectorId,
    reset,
  ]);

  return <connectorFormContext.Provider value={ctx}>{children}</connectorFormContext.Provider>;
};

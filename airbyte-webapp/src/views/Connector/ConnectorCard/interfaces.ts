import React from "react";

import { ConnectorDefinition, ConnectorDefinitionSpecification, ConnectorT } from "../../../core/domain/connector";
import { SynchronousJobRead } from "../../../core/request/AirbyteClient";
import { ServiceFormValues } from "../ServiceForm";

export interface ConnectorCardProvidedProps {
  onServiceSelect?: (id: string) => void;
  fetchingConnectorError?: Error | null;
  formId?: string;
  onSubmit: (values: ServiceFormValues) => Promise<void> | void;
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  isLoading?: boolean;
  formValues?: Partial<ServiceFormValues>;
  successMessage?: React.ReactNode;
  onDelete?: () => Promise<unknown>;
}

export interface ConnectorCardBaseProps extends ConnectorCardProvidedProps {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
}

export interface ConnectorCardCreateProps extends ConnectorCardBaseProps {
  isEditMode?: false;
}

export interface ConnectorCardEditProps extends ConnectorCardBaseProps {
  isEditMode: true;
  connector: ConnectorT;
}

export type ConnectorCardProps = ConnectorCardCreateProps | ConnectorCardEditProps;

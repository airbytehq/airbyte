import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import useRouter from "hooks/useRouter";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";

interface DestinationFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  destinationDefinitions: DestinationDefinitionRead[];
  hasSuccess?: boolean;
  error?: JSX.Element | string | null;
  formValues: ServiceFormValues;
  onShowLoading?: (isLoading: boolean, formValues: ServiceFormValues, error: JSX.Element | string | null) => void;
  onBack?: () => void;
}

const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
  );
};

export const DestinationForm: React.FC<DestinationFormProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  formValues,
  // afterSelectConnector,
  onShowLoading,
  onBack,
}) => {
  const { location } = useRouter();

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : null
  );

  const {
    data: destinationDefinitionSpecification,
    error: destinationDefinitionError,
    isLoading,
  } = useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId);
    // const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);
    // if (afterSelectConnector) {
    //   afterSelectConnector();
    // }
  };

  const onSubmitForm = async (values: { name: string; serviceType: string }) => {
    await onSubmit({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
      onSubmit={onSubmitForm}
      formType="destination"
      availableServices={destinationDefinitions}
      selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
      hasSuccess={hasSuccess}
      errorMessage={error}
      isLoading={isLoading}
      formValues={destinationDefinitionId ? { ...formValues, serviceType: destinationDefinitionId } : undefined}
      title={<FormattedMessage id="onboarding.destinationSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
      onShowLoading={onShowLoading}
      onBack={onBack}
    />
  );
};

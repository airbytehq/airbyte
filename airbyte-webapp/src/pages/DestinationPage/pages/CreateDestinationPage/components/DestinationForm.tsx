import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { generateMessageFromError, FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { FrequentlyUsedDestinations, StartWithDestination } from "views/Connector/ServiceForm";

import styles from "./DestinationForm.module.scss";

interface DestinationFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  destinationDefinitions: DestinationDefinitionRead[];
  hasSuccess?: boolean;
  error?: FormError | null;
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
}) => {
  const location = useLocation();

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
  };

  const onSubmitForm = async (values: { name: string; serviceType: string }) => {
    onSubmit({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? generateMessageFromError(error) : null;

  const frequentlyUsedDestinationsComponent = !isLoading && !destinationDefinitionId && (
    <FrequentlyUsedDestinations onDestinationSelect={onDropDownSelect} availableServices={destinationDefinitions} />
  );
  const startWithDestinationComponent = !isLoading && !destinationDefinitionId && (
    <div className={styles.startWithDestinationContainer}>
      <StartWithDestination onDestinationSelect={onDropDownSelect} availableServices={destinationDefinitions} />
    </div>
  );

  return (
    <>
      <ConnectorCard
        onServiceSelect={onDropDownSelect}
        fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
        onSubmit={onSubmitForm}
        formType="destination"
        additionalSelectorComponent={frequentlyUsedDestinationsComponent}
        availableServices={destinationDefinitions}
        selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        isLoading={isLoading}
        formValues={destinationDefinitionId ? { serviceType: destinationDefinitionId } : undefined}
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
        jobInfo={LogsRequestError.extractJobInfo(error)}
      />
      {startWithDestinationComponent}
    </>
  );
};

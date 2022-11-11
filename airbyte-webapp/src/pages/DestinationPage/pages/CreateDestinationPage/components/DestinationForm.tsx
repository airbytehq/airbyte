import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useExperiment } from "hooks/services/Experiment";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { generateMessageFromError, FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ConnectorCardValues, FrequentlyUsedConnectors, StartWithDestination } from "views/Connector/ConnectorForm";

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

  const onSubmitForm = async (values: ConnectorCardValues) => {
    onSubmit({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? generateMessageFromError(error) : null;

  const frequentlyUsedDestinationIds = useExperiment("connector.frequentlyUsedDestinationIds", [
    "22f6c74f-5699-40ff-833c-4a879ea40133",
    "424892c4-daac-4491-b35d-c6688ba547ba",
  ]);
  const frequentlyUsedDestinationsComponent = !isLoading && !destinationDefinitionId && (
    <FrequentlyUsedConnectors
      connectorType="destination"
      onConnectorSelect={onDropDownSelect}
      availableServices={destinationDefinitions}
      connectorIds={frequentlyUsedDestinationIds}
    />
  );
  const startWithDestinationComponent = !isLoading && !destinationDefinitionId && (
    <div className={styles.startWithDestinationContainer}>
      <StartWithDestination onDestinationSelect={onDropDownSelect} availableServices={destinationDefinitions} />
    </div>
  );

  return (
    <>
      <ConnectorCard
        formType="destination"
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
        isLoading={isLoading}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
        availableConnectorDefinitions={destinationDefinitions}
        onConnectorDefinitionSelect={onDropDownSelect}
        selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
        onSubmit={onSubmitForm}
        jobInfo={LogsRequestError.extractJobInfo(error)}
        additionalSelectorComponent={frequentlyUsedDestinationsComponent}
      />
      {startWithDestinationComponent}
    </>
  );
};

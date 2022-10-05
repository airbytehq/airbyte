import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { Action, Namespace } from "core/analytics";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { generateMessageFromError, FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { FrequentlyUsedDestinations } from "views/Connector/ServiceForm/components/FrequentlyUsedDestinations";
import { StartWithDestination } from "views/Connector/ServiceForm/components/StartWithDestination/StartWithDestination";

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
  afterSelectConnector,
}) => {
  const location = useLocation();
  const analyticsService = useAnalyticsService();

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

    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    analyticsService.track(Namespace.DESTINATION, Action.SELECT, {
      actionDescription: "Destination connector type selected",
      connector_destination: connector?.name,
      connector_destination_definition_id: destinationDefinitionId,
    });
  };

  const onSubmitForm = async (values: { name: string; serviceType: string }) => {
    await onSubmit({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? generateMessageFromError(error) : null;

  // FIXME: need to fix bugs:
  //  - after opening the create form and go back - the UnsavedChanges Modal appear
  //  - need to disable select service type dropdown on formSubmit
  const frequentlyUsedDestinationsComponent = !isLoading && !destinationDefinitionId && (
    <FrequentlyUsedDestinations onServiceSelect={onDropDownSelect} availableServices={destinationDefinitions} />
  );
  const startWithDestinationComponent = !isLoading && !destinationDefinitionId && (
    <StartWithDestination onServiceSelect={onDropDownSelect} availableServices={destinationDefinitions} />
  );

  console.log(!destinationDefinitions.length && !isLoading && !destinationDefinitionId);

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
      onSubmit={onSubmitForm}
      formType="destination"
      additionalDropdownComponent={frequentlyUsedDestinationsComponent}
      intermediateComponent={startWithDestinationComponent}
      availableServices={destinationDefinitions}
      selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
      hasSuccess={hasSuccess}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={destinationDefinitionId ? { serviceType: destinationDefinitionId } : undefined}
      title={<FormattedMessage id="onboarding.destinationSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

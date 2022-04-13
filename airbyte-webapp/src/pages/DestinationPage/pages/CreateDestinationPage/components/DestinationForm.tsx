import React from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinition, DestinationDefinitionSpecification } from "core/domain/connector";
import { LogsRequestError } from "core/request/LogsRequestError";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";

type DestinationFormProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  destinationDefinitions: DestinationDefinition[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
  setDestinationDefinitionId: React.Dispatch<React.SetStateAction<string | null>> | null;
  destinationDefinitionSpecification: DestinationDefinitionSpecification | undefined;
  destinationDefinitionError: Error | null;
  isLoading: boolean;
};

const DestinationForm: React.FC<DestinationFormProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  afterSelectConnector,
  setDestinationDefinitionId,
  destinationDefinitionSpecification,
  destinationDefinitionError,
  isLoading,
}) => {
  const trackNewDestinationAction = useTrackAction(TrackActionType.NEW_DESTINATION);

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId && setDestinationDefinitionId(destinationDefinitionId);
    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    trackNewDestinationAction("Select a connector", {
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

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      fetchingConnectorError={destinationDefinitionError}
      onSubmit={onSubmitForm}
      formType="destination"
      availableServices={destinationDefinitions}
      selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
      hasSuccess={hasSuccess}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={
        destinationDefinitionSpecification
          ? { serviceType: destinationDefinitionSpecification.destinationDefinitionId }
          : undefined
      }
      title={<FormattedMessage id="onboarding.destinationSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

export default DestinationForm;

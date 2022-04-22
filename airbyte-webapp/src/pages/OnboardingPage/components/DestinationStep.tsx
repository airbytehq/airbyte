import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { JobInfo } from "core/domain/job";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";

import HighlightedText from "./HighlightedText";
import TitlesBlock from "./TitlesBlock";

type Props = {
  onNextStep: () => void;
  onSuccess: () => void;
};

const DestinationStep: React.FC<Props> = ({ onNextStep, onSuccess }) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string | null>(null);
  const { data: destinationDefinitionSpecification, isLoading } =
    useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);
  const { destinationDefinitions } = useDestinationDefinitionList();
  const [successRequest, setSuccessRequest] = useState(false);
  const [error, setError] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const { mutateAsync: createDestination } = useCreateDestination();
  const analyticsService = useAnalyticsService();

  const getDestinationDefinitionById = (id: string) =>
    destinationDefinitions.find((item) => item.destinationDefinitionId === id);

  const onSubmitDestinationStep = async (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setError(null);
    const destinationConnector = getDestinationDefinitionById(values.serviceType);

    try {
      await createDestination({
        values,
        destinationConnector,
      });

      setSuccessRequest(true);
      onSuccess();
      setTimeout(() => {
        setSuccessRequest(false);
        onNextStep();
      }, 2000);
    } catch (e) {
      setError(e);
    }
  };

  const onDropDownSelect = (destinationDefinitionId: string) => {
    const destinationConnector = getDestinationDefinitionById(destinationDefinitionId);
    analyticsService.track("New Destination - Action", {
      action: "Select a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id: destinationConnector?.destinationDefinitionId,
    });

    setError(null);
    setDestinationDefinitionId(destinationDefinitionId);
  };
  const onSubmitForm = async (values: { name: string; serviceType: string }) => {
    await onSubmitDestinationStep({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createFirstDestination"
            values={{
              name: (name: React.ReactNode[]) => <HighlightedText>{name}</HighlightedText>,
            }}
          />
        }
      >
        <FormattedMessage id="onboarding.createFirstDestination.text" />
      </TitlesBlock>
      <ConnectorCard
        full
        formType="destination"
        onServiceSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        hasSuccess={successRequest}
        availableServices={destinationDefinitions}
        errorMessage={errorMessage}
        selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
        isLoading={isLoading}
      />
    </>
  );
};

export default DestinationStep;

import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { LogsRequestError } from "core/request/LogsRequestError";

import { useDestinationDefinitionSpecificationLoad } from "hooks/services/useDestinationHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinition } from "core/domain/connector";

import { ConnectorCard } from "views/Connector/ConnectorCard";
import TitlesBlock from "./TitlesBlock";
import HighlightedText from "./HighlightedText";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";

type IProps = {
  availableServices: DestinationDefinition[];
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  hasSuccess?: boolean;
  error?: null | { message?: string; status?: number };
  afterSelectConnector?: () => void;
};

const DestinationStep: React.FC<IProps> = ({
  onSubmit,
  availableServices,
  hasSuccess,
  error,
  afterSelectConnector,
}) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState("");
  const {
    destinationDefinitionSpecification,
    isLoading,
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);

  const analyticsService = useAnalyticsService();

  const onDropDownSelect = (destinationDefinition: string) => {
    const destinationConnector = availableServices.find(
      (s) => s.destinationDefinitionId === destinationDefinition
    );
    analyticsService.track("New Destination - Action", {
      action: "Select a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId,
    });

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    setDestinationDefinitionId(destinationDefinition);
  };
  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      destinationDefinitionId:
        destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? createFormErrorMessage(error) : "";

  return (
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createFirstDestination"
            values={{
              name: (...name: React.ReactNode[]) => (
                <HighlightedText>{name}</HighlightedText>
              ),
            }}
          />
        }
      >
        <FormattedMessage id="onboarding.createFirstDestination.text" />
      </TitlesBlock>
      <ConnectorCard
        full
        jobInfo={LogsRequestError.extractJobInfo(error)}
        formType="destination"
        allowChangeConnector
        onServiceSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        hasSuccess={hasSuccess}
        availableServices={availableServices}
        errorMessage={errorMessage}
        selectedConnector={destinationDefinitionSpecification}
        isLoading={isLoading}
      />
    </>
  );
};

export default DestinationStep;

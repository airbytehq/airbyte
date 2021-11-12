import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import { JobsLogItem } from "components/JobItem";

import { useDestinationDefinitionSpecificationLoad } from "hooks/services/useDestinationHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

import TitlesBlock from "./TitlesBlock";
import HighlightedText from "./HighlightedText";
import { useAnalytics } from "hooks/useAnalytics";

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
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const DestinationStep: React.FC<IProps> = ({
  onSubmit,
  availableServices,
  hasSuccess,
  error,
  jobInfo,
  afterSelectConnector,
}) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState("");
  const {
    destinationDefinitionSpecification,
    isLoading,
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);

  const analyticsService = useAnalytics();

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
      <ContentCard full>
        <ServiceForm
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
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default DestinationStep;

import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import ConnectionBlock from "components/ConnectionBlock";
import { JobsLogItem } from "components/JobItem";

import SourceDefinitionResource from "core/resources/SourceDefinition";
import { useDestinationDefinitionSpecificationLoad } from "hooks/services/useDestinationHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

import SkipOnboardingButton from "./SkipOnboardingButton";
import { useAnalytics } from "hooks/useAnalytics";

type IProps = {
  availableServices: DestinationDefinition[];
  currentSourceDefinitionId: string;
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
  currentSourceDefinitionId,
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
  const currentSource = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: currentSourceDefinitionId,
  });
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
      <ConnectionBlock
        itemFrom={{ name: currentSource.name, icon: currentSource.icon }}
      />
      <ContentCard
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          formType="destination"
          additionBottomControls={
            <SkipOnboardingButton step="destination connection" />
          }
          allowChangeConnector
          onServiceSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          hasSuccess={hasSuccess}
          availableServices={availableServices}
          errorMessage={errorMessage}
          specifications={
            destinationDefinitionSpecification?.connectionSpecification
          }
          documentationUrl={
            destinationDefinitionSpecification?.documentationUrl
          }
          isLoading={isLoading}
        />
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default DestinationStep;

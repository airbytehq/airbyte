import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import ContentCard from "components/ContentCard";
import ServiceForm from "components/ServiceForm";
import ConnectionBlock from "components/ConnectionBlock";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import usePrepareDropdownLists from "./usePrepareDropdownLists";
import { useDestinationDefinitionSpecificationLoad } from "components/hooks/services/useDestinationHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { JobInfo } from "core/resources/Scheduler";
import { JobsLogItem } from "components/JobItem";
import SkipOnboardingButton from "./SkipOnboardingButton";
import { ConnectionConfiguration } from "core/domain/connection";

type IProps = {
  dropDownData: { value: string; text: string; icon: string }[];
  hasSuccess?: boolean;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  error?: null | { message?: string; status?: number };
  currentSourceDefinitionId: string;
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const DestinationStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  error,
  currentSourceDefinitionId,
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
  const { getDestinationDefinitionById } = usePrepareDropdownLists();

  const onDropDownSelect = (sourceId: string) => {
    const destinationConnector = getDestinationDefinitionById(sourceId);
    AnalyticsService.track("New Destination - Action", {
      action: "Select a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId,
    });

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    setDestinationDefinitionId(sourceId);
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
          additionBottomControls={
            <SkipOnboardingButton step="destination connection" />
          }
          allowChangeConnector
          onDropDownSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          hasSuccess={hasSuccess}
          formType="destination"
          availableServices={dropDownData}
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

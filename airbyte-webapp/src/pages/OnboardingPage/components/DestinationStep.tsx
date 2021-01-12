import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import ConnectionBlock from "../../../components/ConnectionBlock";
import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import usePrepareDropdownLists from "./usePrepareDropdownLists";
import { Destination } from "../../../core/resources/Destination";
import { useDestinationDefinitionSpecificationLoad } from "../../../components/hooks/services/useDestinationHook";
import { IDataItem } from "../../../components/DropDown/components/ListItem";
import { createFormErrorMessage } from "../../../utils/errorStatusMessage";
import { JobInfo } from "../../../core/resources/Scheduler";
import { JobsLogItem } from "../../../components/JobItem";

type IProps = {
  destination?: Destination;
  dropDownData: IDataItem[];
  hasSuccess?: boolean;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: any;
  }) => void;
  errorStatus?: number;
  currentSourceDefinitionId: string;
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const DestinationStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorStatus,
  currentSourceDefinitionId,
  destination,
  jobInfo,
  afterSelectConnector
}) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    destination?.destinationDefinitionId || ""
  );
  const {
    destinationDefinitionSpecification,
    isLoading
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);
  const currentSource = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: currentSourceDefinitionId
  });
  const { getDestinationDefinitionById } = usePrepareDropdownLists();

  const onDropDownSelect = (sourceId: string) => {
    const destinationConnector = getDestinationDefinitionById(sourceId);
    AnalyticsService.track("New Destination - Action", {
      action: "Select a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId
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
        destinationDefinitionSpecification?.destinationDefinitionId
    });
  };

  const errorMessage = createFormErrorMessage(errorStatus);

  return (
    <>
      <ConnectionBlock itemFrom={{ name: currentSource.name }} />
      <ContentCard
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          allowChangeConnector
          onDropDownSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          hasSuccess={hasSuccess}
          formType="destination"
          dropDownData={dropDownData}
          errorMessage={errorMessage}
          specifications={
            destinationDefinitionSpecification?.connectionSpecification
          }
          documentationUrl={
            destinationDefinitionSpecification?.documentationUrl
          }
          isLoading={isLoading}
          formValues={
            destination
              ? {
                  ...destination.connectionConfiguration,
                  name: destination.name,
                  serviceType: destination.destinationDefinitionId
                }
              : null
          }
        />
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default DestinationStep;

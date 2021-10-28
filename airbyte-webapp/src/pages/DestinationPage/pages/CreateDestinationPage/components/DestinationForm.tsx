import React, { useRef, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionSpecificationLoad } from "hooks/services/useDestinationHook";
import { JobInfo } from "core/resources/Scheduler";
import { JobsLogItem } from "components/JobItem";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import { useAnalytics } from "hooks/useAnalytics";
import useDocumentation from "hooks/services/useDocumentation";
import SideView, { SideViewRef } from "components/SideView/SideView";
import { Markdown } from "components/Markdown";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  destinationDefinitions: DestinationDefinition[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const DestinationForm: React.FC<IProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  jobInfo,
  afterSelectConnector,
}) => {
  const sideViewRef = useRef<SideViewRef>({} as SideViewRef);

  const { location } = useRouter();
  const analyticsService = useAnalytics();

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    location.state?.destinationDefinitionId || ""
  );
  const {
    destinationDefinitionSpecification,
    isLoading,
    sourceDefinitionError,
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);

  const { data: destinationDefinitionDocs } = useDocumentation(
    destinationDefinitionSpecification?.documentationUrl || ""
  );

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId);
    const connector = destinationDefinitions.find(
      (item) => item.destinationDefinitionId === destinationDefinitionId
    );

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    analyticsService.track("New Destination - Action", {
      action: "Select a connector",
      connector_destination_definition: connector?.name,
      connector_destination_definition_id: destinationDefinitionId,
    });
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

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <>
      <SideView ref={sideViewRef}>
        <Markdown content={destinationDefinitionDocs} />
      </SideView>
      <ContentCard
        actions={
          !!destinationDefinitionDocs && (
            <Button secondary onClick={sideViewRef?.current.open}>
              <FormattedMessage id="form.setupGuide" />
            </Button>
          )
        }
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          onServiceSelect={onDropDownSelect}
          fetchingConnectorError={sourceDefinitionError}
          onSubmit={onSubmitForm}
          formType="destination"
          availableServices={destinationDefinitions}
          selectedConnector={destinationDefinitionSpecification}
          hasSuccess={hasSuccess}
          errorMessage={errorMessage}
          isLoading={isLoading}
          formValues={
            destinationDefinitionId
              ? { serviceType: destinationDefinitionId }
              : undefined
          }
          allowChangeConnector
        />
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default DestinationForm;

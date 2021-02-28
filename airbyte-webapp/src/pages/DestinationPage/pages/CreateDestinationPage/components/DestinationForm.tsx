import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "components/ContentCard";
import ServiceForm from "components/ServiceForm";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import config from "config";
import useRouter from "components/hooks/useRouterHook";
import { useDestinationDefinitionSpecificationLoad } from "components/hooks/services/useDestinationHook";
import { IDataItem } from "components/DropDown/components/ListItem";
import { JobInfo } from "core/resources/Scheduler";
import { JobsLogItem } from "components/JobItem";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  dropDownData: IDataItem[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const DestinationForm: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  error,
  hasSuccess,
  jobInfo,
  afterSelectConnector,
}) => {
  const { location } = useRouter();

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    location.state?.destinationDefinitionId || ""
  );
  const {
    destinationDefinitionSpecification,
    isLoading,
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);
  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId);
    const connector = dropDownData.find(
      (item) => item.value === destinationDefinitionId
    );

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    AnalyticsService.track("New Destination - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_destination_definition: connector?.text,
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
    <ContentCard title={<FormattedMessage id="onboarding.destinationSetUp" />}>
      <ServiceForm
        onDropDownSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        formType="destination"
        dropDownData={dropDownData}
        specifications={
          destinationDefinitionSpecification?.connectionSpecification
        }
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        isLoading={isLoading}
        formValues={
          destinationDefinitionId
            ? { serviceType: destinationDefinitionId, name: "" }
            : undefined
        }
        allowChangeConnector
      />
      <JobsLogItem jobInfo={jobInfo} />
    </ContentCard>
  );
};

export default DestinationForm;

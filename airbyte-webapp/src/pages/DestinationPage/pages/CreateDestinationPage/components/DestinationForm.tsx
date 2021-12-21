import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionSpecificationLoad } from "hooks/services/useDestinationHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { DestinationDefinition } from "core/domain/connector";

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
  afterSelectConnector?: () => void;
};

const DestinationForm: React.FC<IProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const analyticsService = useAnalyticsService();

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    location.state?.destinationDefinitionId || ""
  );
  const {
    destinationDefinitionSpecification,
    isLoading,
    sourceDefinitionError,
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);

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
    <ConnectorCard
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
      title={<FormattedMessage id="onboarding.destinationSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

export default DestinationForm;

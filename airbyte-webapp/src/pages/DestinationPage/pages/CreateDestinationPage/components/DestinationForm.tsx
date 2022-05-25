import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import useRouter from "hooks/useRouter";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

interface DestinationFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  destinationDefinitions: DestinationDefinitionRead[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
  afterSelectConnector?: () => void;
}

const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
  );
};

export const DestinationForm: React.FC<DestinationFormProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const trackNewDestinationAction = useTrackAction(TrackActionType.NEW_DESTINATION);

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : null
  );
  const {
    data: destinationDefinitionSpecification,
    isLoading,
    error: destinationDefinitionError,
  } = useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);
  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDocumentationPanelOpen(false);
    setDestinationDefinitionId(destinationDefinitionId);
    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);
    setDocumentationUrl(connector?.documentationUrl ?? "");

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
      fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
      onSubmit={onSubmitForm}
      formType="destination"
      availableServices={destinationDefinitions}
      selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
      hasSuccess={hasSuccess}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={destinationDefinitionId ? { serviceType: destinationDefinitionId } : undefined}
      title={<FormattedMessage id="onboarding.destinationSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

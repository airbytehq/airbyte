import React, { useEffect, useState } from "react";

import { Action, Namespace } from "core/analytics";
import { ConnectionConfiguration } from "core/domain/connection";
import { JobInfo } from "core/domain/job";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

interface Props {
  onNextStep: () => void;
  onSuccess: () => void;
}

const DestinationStep: React.FC<Props> = ({ onNextStep, onSuccess }) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string | null>(null);
  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
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

  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

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
    setDocumentationPanelOpen(false);
    const destinationConnector = getDestinationDefinitionById(destinationDefinitionId);
    setDocumentationUrl(destinationConnector?.documentationUrl || "");

    analyticsService.track(Namespace.DESTINATION, Action.SELECT, {
      actionDescription: "Destination connector type selected",
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
  );
};

export default DestinationStep;

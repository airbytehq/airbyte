import React, { useEffect, useState } from "react";

import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { generateMessageFromError, FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorCardValues } from "views/Connector/ConnectorForm";

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
  const [error, setError] = useState<FormError | null>(null);

  const { mutateAsync: createDestination } = useCreateDestination();

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

    setError(null);
    setDestinationDefinitionId(destinationDefinitionId);
  };
  const onSubmitForm = async (values: ConnectorCardValues) => {
    await onSubmitDestinationStep({
      ...values,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? generateMessageFromError(error) : null;

  return (
    <ConnectorCard
      full
      formType="destination"
      isLoading={isLoading}
      hasSuccess={successRequest}
      errorMessage={errorMessage}
      availableConnectorDefinitions={destinationDefinitions}
      onConnectorDefinitionSelect={onDropDownSelect}
      selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
      onSubmit={onSubmitForm}
    />
  );
};

export default DestinationStep;

import React, { useEffect, useState } from "react";

import { ConnectionConfiguration } from "core/domain/connection";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useCreateSource } from "hooks/services/useSourceHook";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { generateMessageFromError, FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorCardValues } from "views/Connector/ConnectorForm";

interface SourcesStepProps {
  onSuccess: () => void;
  onNextStep: () => void;
}

const SourceStep: React.FC<SourcesStepProps> = ({ onNextStep, onSuccess }) => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(null);
  const [successRequest, setSuccessRequest] = useState(false);
  const [error, setError] = useState<FormError | null>(null);

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
  const { mutateAsync: createSource } = useCreateSource();

  const getSourceDefinitionById = (id: string) => sourceDefinitions.find((item) => item.sourceDefinitionId === id);

  const { data: sourceDefinitionSpecification, isLoading } =
    useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);

  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    sourceId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setError(null);
    const sourceConnector = getSourceDefinitionById(values.serviceType);

    if (!sourceConnector) {
      // Unsure if this can happen, but the types want it defined
      throw new Error("No Connector Found");
    }

    try {
      await createSource({ values, sourceConnector });

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

  const onServiceSelect = (sourceId: string) => {
    setDocumentationPanelOpen(false);
    const sourceDefinition = getSourceDefinitionById(sourceId);
    setDocumentationUrl(sourceDefinition?.documentationUrl || "");

    setError(null);
    setSourceDefinitionId(sourceId);
  };

  const onSubmitForm = async (values: ConnectorCardValues) =>
    onSubmitSourceStep({
      ...values,
    });

  const errorMessage = error ? generateMessageFromError(error) : "";

  return (
    <ConnectorCard
      full
      formType="source"
      isLoading={isLoading}
      hasSuccess={successRequest}
      errorMessage={errorMessage}
      availableConnectorDefinitions={sourceDefinitions}
      onConnectorDefinitionSelect={onServiceSelect}
      selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      onSubmit={onSubmitForm}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

export default SourceStep;

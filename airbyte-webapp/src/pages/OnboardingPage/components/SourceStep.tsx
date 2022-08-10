import React, { useEffect, useState } from "react";

import { Action, Namespace } from "core/analytics";
import { ConnectionConfiguration } from "core/domain/connection";
import { JobInfo } from "core/domain/job";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCreateSource } from "hooks/services/useSourceHook";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

interface SourcesStepProps {
  onSuccess: () => void;
  onNextStep: () => void;
}

const SourceStep: React.FC<SourcesStepProps> = ({ onNextStep, onSuccess }) => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(null);
  const [successRequest, setSuccessRequest] = useState(false);
  const [error, setError] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
  const { mutateAsync: createSource } = useCreateSource();

  const analyticsService = useAnalyticsService();

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

    analyticsService.track(Namespace.SOURCE, Action.SELECT, {
      actionDescription: "Source connector type selected",
      connector_source: sourceDefinition?.name,
      connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
    });

    setError(null);
    setSourceDefinitionId(sourceId);
  };

  const onSubmitForm = async (values: { name: string; serviceType: string }) =>
    onSubmitSourceStep({
      ...values,
    });

  const errorMessage = error ? createFormErrorMessage(error) : "";

  return (
    <ConnectorCard
      full
      jobInfo={LogsRequestError.extractJobInfo(error)}
      onServiceSelect={onServiceSelect}
      onSubmit={onSubmitForm}
      formType="source"
      availableServices={sourceDefinitions}
      hasSuccess={successRequest}
      errorMessage={errorMessage}
      selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      isLoading={isLoading}
    />
  );
};

export default SourceStep;

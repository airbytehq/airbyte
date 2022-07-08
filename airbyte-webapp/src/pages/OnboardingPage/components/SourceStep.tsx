import React, { useEffect, useMemo, useState } from "react";

import { ContentCard } from "components";
import { SelectServiceType } from "components/SelectServiceType/SelectServiceType";

import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { JobInfo } from "core/domain/job";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useCreateSource } from "hooks/services/useSourceHook";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./StepsCommonStyling.module.scss";

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

  const trackNewSourceAction = useTrackAction(TrackActionType.NEW_SOURCE);

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
    trackNewSourceAction("Select a connector", {
      connector_source: sourceDefinition?.name,
      connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
    });

    setError(null);
    setSourceDefinitionId(sourceId);
  };

  const onSubmitForm = async (values: { name: string }) =>
    onSubmitSourceStep({
      ...values,
      serviceType: "asdfsadf",
    });

  const errorMessage = error ? createFormErrorMessage(error) : "";

  const selectedService = useMemo(
    () => sourceDefinitions.find((s) => Connector.id(s) === sourceDefinitionId),
    [sourceDefinitions, sourceDefinitionId]
  );

  return (
    <>
      <ContentCard className={styles.contentCard}>
        <SelectServiceType
          formType="source"
          value={sourceDefinitionId}
          onChangeServiceType={onServiceSelect}
          availableServices={sourceDefinitions}
        />
      </ContentCard>

      {selectedService && (
        <ConnectorCard
          full
          jobInfo={LogsRequestError.extractJobInfo(error)}
          onSubmit={onSubmitForm}
          formType="source"
          hasSuccess={successRequest}
          errorMessage={errorMessage}
          selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
          isLoading={isLoading}
          selectedService={selectedService}
        />
      )}
    </>
  );
};

export default SourceStep;

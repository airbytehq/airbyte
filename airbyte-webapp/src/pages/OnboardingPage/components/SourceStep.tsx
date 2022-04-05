import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import HighlightedText from "./HighlightedText";
import TitlesBlock from "./TitlesBlock";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useCreateSource } from "hooks/services/useSourceHook";
import { JobInfo } from "core/domain/job";

type IProps = {
  onSuccess: () => void;
  onNextStep: () => void;
};

const SourceStep: React.FC<IProps> = ({ onNextStep, onSuccess }) => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(
    null
  );
  const [successRequest, setSuccessRequest] = useState(false);
  const [error, setError] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const { mutateAsync: createSource } = useCreateSource();

  const analyticsService = useAnalyticsService();

  const getSourceDefinitionById = (id: string) =>
    sourceDefinitions.find((item) => item.sourceDefinitionId === id);

  const {
    data: sourceDefinitionSpecification,
    isLoading,
  } = useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    sourceId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setError(null);
    const sourceConnector = getSourceDefinitionById(values.serviceType);

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
    const sourceDefinition = getSourceDefinitionById(sourceId);

    analyticsService.track("New Source - Action", {
      action: "Select a connector",
      connector_source: sourceDefinition?.name,
      connector_source_id: sourceDefinition?.sourceDefinitionId,
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
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createFirstSource"
            values={{
              name: (name: React.ReactNode) => (
                <HighlightedText>{name}</HighlightedText>
              ),
            }}
          />
        }
      >
        <FormattedMessage id="onboarding.createFirstSource.text" />
      </TitlesBlock>
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
    </>
  );
};

export default SourceStep;

import React, { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useGetSource } from "hooks/services/useSourceHook";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";

interface CloneSourceFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  sourceDefinitions: SourceDefinitionReadWithLatestTag[];
  hasSuccess?: boolean;
  sourceCloneId: string;
  error?: { message?: string; status?: number } | null;
}

export const CloneSourceForm: React.FC<CloneSourceFormProps> = ({
  onSubmit,
  sourceDefinitions,
  error,
  hasSuccess,
  sourceCloneId,
  afterSelectConnector,
}) => {
  const trackNewSourceAction = useTrackAction(TrackActionType.NEW_SOURCE);
  const source = useGetSource(sourceCloneId);

  const [sourceDefinitionId, setSourceDefinitionId] = useState<string>(source.sourceDefinitionId);

  const {
    data: sourceDefinitionSpecification,
    error: sourceDefinitionError,
    isLoading,
  } = useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);

  const onDropDownSelect = useCallback(
    (sourceDefinitionId: string) => {
      setSourceDefinitionId(sourceDefinitionId);

      const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === sourceDefinitionId);

      if (afterSelectConnector) {
        afterSelectConnector();
      }

      trackNewSourceAction("Select a connector", {
        connector_source: connector?.name,
        connector_source_definition_id: sourceDefinitionId,
      });
    },
    [afterSelectConnector, sourceDefinitions, trackNewSourceAction]
  );

  const onSubmitForm = async (values: ServiceFormValues) => {
    await onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId,
    });
  };

  const errorMessage = error ? createFormErrorMessage(error) : null;
  const formValues = {
    serviceType: source.sourceDefinitionId,
    name: source.name,
    connectionConfiguration: source.connectionConfiguration,
  };

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      onSubmit={onSubmitForm}
      formType="source"
      availableServices={sourceDefinitions}
      selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      hasSuccess={hasSuccess}
      fetchingConnectorError={sourceDefinitionError instanceof Error ? sourceDefinitionError : null}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={formValues}
      title={<FormattedMessage id="onboarding.sourceSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
      isClonningMode
      connector={source}
    />
  );
};

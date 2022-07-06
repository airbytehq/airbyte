import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useGetSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";

interface SourceFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  sourceDefinitions: SourceDefinitionReadWithLatestTag[];
  hasSuccess?: boolean;
  sourceCloneId?: string;
  error?: { message?: string; status?: number } | null;
}

const hasSourceDefinitionId = (state: unknown): state is { sourceDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { sourceDefinitionId?: string }).sourceDefinitionId === "string"
  );
};

export const SourceForm: React.FC<SourceFormProps> = ({
  onSubmit,
  sourceDefinitions,
  error,
  hasSuccess,
  sourceCloneId,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const trackNewSourceAction = useTrackAction(TrackActionType.NEW_SOURCE);

  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(
    hasSourceDefinitionId(location.state) ? location.state.sourceDefinitionId : null
  );

  const {
    data: sourceDefinitionSpecification,
    error: sourceDefinitionError,
    isLoading,
  } = useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);
  const source = useGetSource(sourceCloneId);

  const onDropDownSelect = (sourceDefinitionId: string) => {
    chooseSource(sourceDefinitionId);
  };

  const chooseSource = useCallback(
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

  const getFormValues = () => {
    if (source) {
      return {
        serviceType: source.sourceDefinitionId,
        name: source.name,
        connectionConfiguration: source.connectionConfiguration,
      };
    }

    return sourceDefinitionId ? { serviceType: sourceDefinitionId, name: "" } : undefined;
  };

  useEffect(() => {
    if (source) {
      chooseSource(source.sourceDefinitionId);
    }
  }, [source, chooseSource]);

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      onSubmit={onSubmitForm}
      formType="source"
      availableServices={sourceDefinitions}
      checkConnectionBeforeSubmit={sourceCloneId ? false : true}
      selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      hasSuccess={hasSuccess}
      fetchingConnectorError={sourceDefinitionError instanceof Error ? sourceDefinitionError : null}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={getFormValues()}
      title={<FormattedMessage id="onboarding.sourceSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

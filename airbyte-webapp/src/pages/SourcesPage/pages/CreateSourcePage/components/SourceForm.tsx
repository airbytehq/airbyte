import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ContentCard } from "components";
import { SelectServiceType } from "components/SelectServiceType/SelectServiceType";
import TitleBlock from "components/TitleBlock/TitleBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { LogsRequestError } from "core/request/LogsRequestError";
import useRouter from "hooks/useRouter";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";

import styles from "./SourceForm.module.scss";

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

  const onDropDownSelect = (sourceDefinitionId: string) => {
    setSourceDefinitionId(sourceDefinitionId);

    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === sourceDefinitionId);

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    trackNewSourceAction("Select a connector", {
      connector_source: connector?.name,
      connector_source_definition_id: sourceDefinitionId,
    });
  };

  const onSubmitForm = async (values: ServiceFormValues) => {
    await onSubmit({
      ...values,
      serviceType: sourceDefinitionId as string,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId,
    });
  };

  const selectedService = useMemo(
    () => sourceDefinitions.find((s) => Connector.id(s) === sourceDefinitionId),
    [sourceDefinitions, sourceDefinitionId]
  );

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <>
      <ContentCard className={styles.contentCard}>
        <TitleBlock title={<FormattedMessage id="onboarding.sourceSetUp" />} />
        <div className={styles.serviceTypeContainer}>
          <SelectServiceType
            formType="source"
            value={sourceDefinitionId}
            onChangeServiceType={onDropDownSelect}
            availableServices={sourceDefinitions}
          />
        </div>
      </ContentCard>
      {selectedService && (
        <ConnectorCard
          onSubmit={onSubmitForm}
          formType="source"
          selectedService={selectedService}
          selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
          hasSuccess={hasSuccess}
          fetchingConnectorError={sourceDefinitionError instanceof Error ? sourceDefinitionError : null}
          errorMessage={errorMessage}
          formValues={{ name: selectedService.name }}
          isLoading={isLoading}
          jobInfo={LogsRequestError.extractJobInfo(error)}
        />
      )}
    </>
  );
};

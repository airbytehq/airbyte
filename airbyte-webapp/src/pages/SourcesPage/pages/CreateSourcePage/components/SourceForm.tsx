import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { BuilderPrompt } from "components/connectorBuilder/BuilderPrompt";
import { Card } from "components/ui/Card";

import { ConnectionConfiguration } from "core/domain/connection";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useExperiment } from "hooks/services/Experiment";
import { RoutePaths } from "pages/routePaths";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { FormError } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ConnectorCardValues } from "views/Connector/ConnectorForm/types";

import styles from "./SourceForm.module.scss";

interface SourceFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => Promise<void>;
  sourceDefinitions: SourceDefinitionReadWithLatestTag[];
  error?: FormError | null;
}

const hasSourceDefinitionId = (state: unknown): state is { sourceDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { sourceDefinitionId?: string }).sourceDefinitionId === "string"
  );
};

export const SourceForm: React.FC<SourceFormProps> = ({ onSubmit, sourceDefinitions, error }) => {
  const location = useLocation();

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
  };

  const onSubmitForm = (values: ConnectorCardValues) => {
    onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId,
    });
  };

  const showBuilderNavigationLinks = useExperiment("connectorBuilder.showNavigationLinks", false);

  return (
    <>
      <ConnectorCard
        formType="source"
        title={<FormattedMessage id="onboarding.sourceSetUp" />}
        description={<FormattedMessage id="sources.description" />}
        isLoading={isLoading}
        fetchingConnectorError={sourceDefinitionError instanceof Error ? sourceDefinitionError : null}
        availableConnectorDefinitions={sourceDefinitions}
        onConnectorDefinitionSelect={onDropDownSelect}
        selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
        selectedConnectorDefinitionId={sourceDefinitionId}
        onSubmit={onSubmitForm}
        jobInfo={LogsRequestError.extractJobInfo(error)}
      />
      {showBuilderNavigationLinks && !sourceDefinitionSpecification && (
        <Card fullWidth className={styles.builderPrompt}>
          <BuilderPrompt builderRoutePath={`../../${RoutePaths.ConnectorBuilder}`} />
        </Card>
      )}
    </>
  );
};

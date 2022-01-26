import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import useRouter from "hooks/useRouter";
import { useSourceDefinitionSpecificationLoad } from "hooks/services/useSourceHook";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { SourceDefinition } from "core/domain/connector";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  sourceDefinitions: SourceDefinition[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
};

const SourceForm: React.FC<IProps> = ({
  onSubmit,
  sourceDefinitions,
  error,
  hasSuccess,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const analyticsService = useAnalyticsService();

  const [sourceDefinitionId, setSourceDefinitionId] = useState(
    location.state?.sourceDefinitionId || ""
  );

  const {
    sourceDefinitionSpecification,
    sourceDefinitionError,
    isLoading,
  } = useSourceDefinitionSpecificationLoad(sourceDefinitionId);

  const onDropDownSelect = (sourceDefinitionId: string) => {
    setSourceDefinitionId(sourceDefinitionId);
    const connector = sourceDefinitions.find(
      (item) => item.sourceDefinitionId === sourceDefinitionId
    );

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    analyticsService.track("New Source - Action", {
      action: "Select a connector",
      connector_source_definition: connector?.name,
      connector_source_definition_id: sourceDefinitionId,
    });
  };

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId,
    });
  };

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <ConnectorCard
      onServiceSelect={onDropDownSelect}
      onSubmit={onSubmitForm}
      formType="source"
      availableServices={sourceDefinitions}
      selectedConnector={sourceDefinitionSpecification}
      hasSuccess={hasSuccess}
      fetchingConnectorError={sourceDefinitionError}
      errorMessage={errorMessage}
      isLoading={isLoading}
      formValues={
        sourceDefinitionId
          ? { serviceType: sourceDefinitionId, name: "" }
          : undefined
      }
      allowChangeConnector
      title={<FormattedMessage id="onboarding.sourceSetUp" />}
      jobInfo={LogsRequestError.extractJobInfo(error)}
    />
  );
};

export default SourceForm;

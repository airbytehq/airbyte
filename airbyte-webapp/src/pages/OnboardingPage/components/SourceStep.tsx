import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { JobInfo } from "core/resources/Scheduler";
import { SourceDefinition } from "core/resources/SourceDefinition";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import { JobsLogItem } from "components/JobItem";

import { useSourceDefinitionSpecificationLoad } from "hooks/services/useSourceHook";

import SkipOnboardingButton from "./SkipOnboardingButton";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { useAnalytics } from "hooks/useAnalytics";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  availableServices: SourceDefinition[];
  hasSuccess?: boolean;
  error?: null | { message?: string; status?: number };
  jobInfo?: JobInfo;
  afterSelectConnector?: () => void;
};

const SourceStep: React.FC<IProps> = ({
  onSubmit,
  availableServices,
  hasSuccess,
  error,
  jobInfo,
  afterSelectConnector,
}) => {
  const [sourceDefinitionId, setSourceDefinitionId] = useState("");
  const analyticsService = useAnalytics();

  const {
    sourceDefinitionSpecification,
    isLoading,
  } = useSourceDefinitionSpecificationLoad(sourceDefinitionId);

  const onServiceSelect = (sourceId: string) => {
    const sourceDefinition = availableServices.find(
      (s) => s.sourceDefinitionId === sourceId
    );

    analyticsService.track("New Source - Action", {
      action: "Select a connector",
      connector_source: sourceDefinition?.name,
      connector_source_id: sourceDefinition?.sourceDefinitionId,
    });

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    setSourceDefinitionId(sourceId);
  };

  const onSubmitForm = async (values: { name: string; serviceType: string }) =>
    onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId,
    });

  const errorMessage = error ? createFormErrorMessage(error) : "";

  return (
    <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
      <ServiceForm
        additionBottomControls={
          <SkipOnboardingButton step="source connection" />
        }
        allowChangeConnector
        onServiceSelect={onServiceSelect}
        onSubmit={onSubmitForm}
        formType="source"
        availableServices={availableServices}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        specifications={sourceDefinitionSpecification?.connectionSpecification}
        documentationUrl={sourceDefinitionSpecification?.documentationUrl}
        isLoading={isLoading}
      />
      <JobsLogItem jobInfo={jobInfo} />
    </ContentCard>
  );
};

export default SourceStep;

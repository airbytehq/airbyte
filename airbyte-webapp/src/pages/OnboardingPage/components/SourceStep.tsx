import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { JobInfo } from "core/resources/Scheduler";
import { SourceDefinition } from "core/resources/SourceDefinition";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import { JobsLogItem } from "components/JobItem";

import { useSourceDefinitionSpecificationLoad } from "hooks/services/useSourceHook";

import { createFormErrorMessage } from "utils/errorStatusMessage";
import { useAnalytics } from "hooks/useAnalytics";
import HighlightedText from "./HighlightedText";
import TitlesBlock from "./TitlesBlock";

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
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createFirstSource"
            values={{
              name: (...name: React.ReactNode[]) => (
                <HighlightedText>{name}</HighlightedText>
              ),
            }}
          />
        }
      >
        <FormattedMessage id="onboarding.createFirstSource.text" />
      </TitlesBlock>
      <ContentCard full>
        <ServiceForm
          allowChangeConnector
          onServiceSelect={onServiceSelect}
          onSubmit={onSubmitForm}
          formType="source"
          availableServices={availableServices}
          hasSuccess={hasSuccess}
          errorMessage={errorMessage}
          selectedConnector={sourceDefinitionSpecification}
          isLoading={isLoading}
        />
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default SourceStep;

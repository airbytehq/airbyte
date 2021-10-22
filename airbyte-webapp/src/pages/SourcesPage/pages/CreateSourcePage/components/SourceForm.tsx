import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import useRouter from "hooks/useRouter";
import { useSourceDefinitionSpecificationLoad } from "hooks/services/useSourceHook";
import { JobInfo } from "core/resources/Scheduler";
import { JobsLogItem } from "components/JobItem";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { useAnalytics } from "hooks/useAnalytics";
import useDocumentation from "hooks/services/useDocumentation";

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
  jobInfo?: JobInfo;
};

const SetupGuide = styled.div`
  background-color: #fff;
  position: absolute;
  height: 100vh;
  width: 60vw;
  top: 0;
  right: 0;
  z-index: 99999;
  box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
    0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);
  padding: 50px;
  overflow: scroll;
`;

const SourceForm: React.FC<IProps> = ({
  onSubmit,
  sourceDefinitions,
  error,
  hasSuccess,
  jobInfo,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const analyticsService = useAnalytics();

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
  const [sg, setSg] = useState<boolean>(false);

  const docs = useDocumentation();

  useEffect(() => {
    if (sourceDefinitionSpecification) {
      docs.mutate(sourceDefinitionSpecification);
    }
  }, [sourceDefinitionSpecification, docs]);

  return (
    <>
      {sg && docs.data && (
        <SetupGuide onClick={() => setSg(false)}>
          <ReactMarkdown remarkPlugins={[remarkGfm]} children={docs.data} />
        </SetupGuide>
      )}
      <ContentCard
        onButtonClick={() => setSg(true)}
        title={<FormattedMessage id="onboarding.sourceSetUp" />}
      >
        <ServiceForm
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
        />
        <JobsLogItem jobInfo={jobInfo} />
      </ContentCard>
    </>
  );
};

export default SourceForm;

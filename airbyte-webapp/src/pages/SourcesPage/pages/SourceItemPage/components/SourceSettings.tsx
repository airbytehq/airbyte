import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { Source } from "../../../../../core/resources/Source";
import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import useSource from "../../../../../components/hooks/services/useSourceHook";
import SourceDefinitionSpecificationResource from "../../../../../core/resources/SourceDefinitionSpecification";
import DeleteBlock from "../../../../../components/DeleteBlock";
import { Connection } from "../../../../../core/resources/Connection";
import { JobInfo } from "../../../../../core/resources/Scheduler";
import { JobsLogItem } from "../../../../../components/JobItem";
import { createFormErrorMessage } from "../../../../../utils/errorStatusMessage";

const Content = styled.div`
  max-width: 813px;
  margin: 18px auto;
`;

type IProps = {
  currentSource: Source;
  connectionsWithSource: Connection[];
};

const SourceSettings: React.FC<IProps> = ({
  currentSource,
  connectionsWithSource
}) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    statusMessage: string | React.ReactNode;
    response: JobInfo;
  } | null>(null);

  const { updateSource, deleteSource } = useSource();

  const sourceDefinitionSpecification = useResource(
    SourceDefinitionSpecificationResource.detailShape(),
    {
      sourceDefinitionId: currentSource.sourceDefinitionId
    }
  );

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(null);
    try {
      await updateSource({
        values,
        sourceId: currentSource.sourceId,
        sourceDefinitionId: currentSource.sourceDefinitionId
      });

      setSaved(true);
    } catch (e) {
      const errorStatusMessage = createFormErrorMessage(e);

      setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage });
    }
  };

  const onDelete = async () => {
    await deleteSource({ connectionsWithSource, source: currentSource });
  };

  return (
    <Content>
      <ContentCard title={<FormattedMessage id="sources.sourceSettings" />}>
        <ServiceForm
          isEditMode
          onSubmit={onSubmit}
          formType="source"
          dropDownData={[
            {
              value: currentSource.sourceDefinitionId || "",
              text: currentSource.sourceName || "",
              img: "/default-logo-catalog.svg"
            }
          ]}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          errorMessage={errorStatusRequest?.statusMessage}
          formValues={{
            ...currentSource,
            serviceType: currentSource.sourceDefinitionId
          }}
          specifications={
            sourceDefinitionSpecification?.connectionSpecification
          }
        />
        <JobsLogItem jobInfo={errorStatusRequest?.response} />
      </ContentCard>
      <DeleteBlock type="source" onDelete={onDelete} />
    </Content>
  );
};

export default SourceSettings;

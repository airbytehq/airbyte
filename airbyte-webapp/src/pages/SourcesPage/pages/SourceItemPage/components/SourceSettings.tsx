import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import useSource from "hooks/services/useSourceHook";
import SourceDefinitionSpecificationResource from "core/resources/SourceDefinitionSpecification";
import DeleteBlock from "components/DeleteBlock";
import { Connection } from "core/resources/Connection";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { Source } from "core/domain/connector";

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
  connectionsWithSource,
}) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(
    null
  );

  const { updateSource, deleteSource, checkSourceConnection } = useSource();

  const sourceDefinitionSpecification = useResource(
    SourceDefinitionSpecificationResource.detailShape(),
    {
      sourceDefinitionId: currentSource.sourceDefinitionId,
    }
  );
  const sourceDefinition = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: currentSource.sourceDefinitionId,
  });

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setErrorStatusRequest(null);
    try {
      await updateSource({
        values,
        sourceId: currentSource.sourceId,
      });

      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  const onRetest = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setErrorStatusRequest(null);
    try {
      await checkSourceConnection({
        values,
        sourceId: currentSource.sourceId,
      });
      setSaved(true);
    } catch (e) {
      const errorStatusMessage = createFormErrorMessage(e);

      setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage });
    }
  };

  const onDelete = () =>
    deleteSource({ connectionsWithSource, source: currentSource });

  return (
    <Content>
      <ConnectorCard
        title={<FormattedMessage id="sources.sourceSettings" />}
        onRetest={onRetest}
        isEditMode
        onSubmit={onSubmit}
        formType="source"
        availableServices={[sourceDefinition]}
        successMessage={saved && <FormattedMessage id="form.changesSaved" />}
        errorMessage={
          errorStatusRequest && createFormErrorMessage(errorStatusRequest)
        }
        formValues={{
          ...currentSource,
          serviceType: currentSource.sourceDefinitionId,
        }}
        selectedConnector={sourceDefinitionSpecification}
        jobInfo={LogsRequestError.extractJobInfo(errorStatusRequest)}
      />
      <DeleteBlock type="source" onDelete={onDelete} />
    </Content>
  );
};

export default SourceSettings;

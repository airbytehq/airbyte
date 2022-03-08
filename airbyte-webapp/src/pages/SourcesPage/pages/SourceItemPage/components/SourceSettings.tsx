import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import useRouter from "hooks/useRouter";
import useSource from "hooks/services/useSourceHook";
import SourceDefinitionSpecificationResource from "core/resources/SourceDefinitionSpecification";
import DeleteBlock from "components/DeleteBlock";
import TitleBlock from "components/TitleBlock";
import { Connection } from "core/resources/Connection";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { Source } from "core/domain/connector";
// import CloneSourceAction from "./CloneSourceAction";

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

  const {
    updateSource,
    deleteSource,
    checkSourceConnection,
    cloneSource,
  } = useSource();
  const { location } = useRouter();

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

  const addLatestSourceIdToLocation = (sourceId: string): string => {
    const breakPaths = location.pathname.split("/");
    breakPaths[breakPaths.length - 1] = sourceId;

    return breakPaths.join("/");
  };

  const onClone = async () => {
    const { sourceId }: Source = await cloneSource({
      sourceId: currentSource.sourceId,
    });

    // Replace/Push functions are not updating the form so had to refresh the page
    window.location.pathname = addLatestSourceIdToLocation(sourceId);
  };

  const onDelete = () =>
    deleteSource({ connectionsWithSource, source: currentSource });

  return (
    <Content>
      <TitleBlock type="source" name={currentSource.name} onClone={onClone} />
      <ConnectorCard
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

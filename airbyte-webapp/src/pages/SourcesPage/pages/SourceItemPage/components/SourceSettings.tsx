import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import useSource from "hooks/services/useSourceHook";
import DeleteBlock from "components/DeleteBlock";
import { Connection } from "core/resources/Connection";
import { ConnectionConfiguration } from "core/domain/connection";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { Source } from "core/domain/connector";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";

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
  const { updateSource, deleteSource } = useSource();

  const sourceDefinitionSpecification = useGetSourceDefinitionSpecification(
    currentSource.sourceDefinitionId
  );

  const sourceDefinition = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: currentSource.sourceDefinitionId,
  });

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) =>
    await updateSource({
      values,
      sourceId: currentSource.sourceId,
    });

  const onDelete = () =>
    deleteSource({ connectionsWithSource, source: currentSource });

  return (
    <Content>
      <ConnectorCard
        title={<FormattedMessage id="sources.sourceSettings" />}
        isEditMode
        onSubmit={onSubmit}
        formType="source"
        connector={currentSource}
        availableServices={[sourceDefinition]}
        formValues={{
          ...currentSource,
          serviceType: currentSource.sourceDefinitionId,
        }}
        selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      />
      <DeleteBlock type="source" onDelete={onDelete} />
    </Content>
  );
};

export default SourceSettings;

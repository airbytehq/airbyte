import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import DeleteBlock from "components/DeleteBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { Source } from "core/domain/connector";
import { useDeleteSource, useUpdateSource } from "hooks/services/useSourceHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";

import { WebBackendConnectionRead } from "../../../../../core/request/GeneratedApi";

const Content = styled.div`
  max-width: 813px;
  margin: 18px auto;
`;

type IProps = {
  currentSource: Source;
  connectionsWithSource: WebBackendConnectionRead[];
};

const SourceSettings: React.FC<IProps> = ({ currentSource, connectionsWithSource }) => {
  const { mutateAsync: updateSource } = useUpdateSource();
  const { mutateAsync: deleteSource } = useDeleteSource();

  const sourceDefinitionSpecification = useGetSourceDefinitionSpecification(currentSource.sourceDefinitionId);

  const sourceDefinition = useSourceDefinition(currentSource?.sourceDefinitionId);

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) =>
    await updateSource({
      values,
      sourceId: currentSource.sourceId,
    });

  const onDelete = () => deleteSource({ connectionsWithSource, source: currentSource });

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

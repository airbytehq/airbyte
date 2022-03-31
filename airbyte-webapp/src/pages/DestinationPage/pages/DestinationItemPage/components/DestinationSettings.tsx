import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import DeleteBlock from "components/DeleteBlock";
import useDestination from "hooks/services/useDestinationHook";
import { Connection } from "core/resources/Connection";
import { ConnectionConfiguration } from "core/domain/connection";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { Connector, Destination } from "core/domain/connector";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";

const Content = styled.div`
  max-width: 813px;
  margin: 19px auto;
`;

type IProps = {
  currentDestination: Destination;
  connectionsWithDestination: Connection[];
};

const DestinationsSettings: React.FC<IProps> = ({
  currentDestination,
  connectionsWithDestination,
}) => {
  const destinationSpecification = useGetDestinationDefinitionSpecification(
    currentDestination.destinationDefinitionId
  );

  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId,
    }
  );

  const { updateDestination, deleteDestination } = useDestination();

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    await updateDestination({
      values,
      destinationId: currentDestination.destinationId,
    });
  };

  const onDelete = () =>
    deleteDestination({
      connectionsWithDestination,
      destination: currentDestination,
    });

  return (
    <Content>
      <ConnectorCard
        isEditMode
        onSubmit={onSubmitForm}
        formType="destination"
        availableServices={[destinationDefinition]}
        formValues={{
          ...currentDestination,
          serviceType: Connector.id(destinationDefinition),
        }}
        connector={currentDestination}
        selectedConnectorDefinitionSpecification={destinationSpecification}
        title={<FormattedMessage id="destination.destinationSettings" />}
      />
      <DeleteBlock type="destination" onDelete={onDelete} />
    </Content>
  );
};

export default DestinationsSettings;

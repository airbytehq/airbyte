import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import DeleteBlock from "components/DeleteBlock";
import useDestination, {
  useDestinationDefinitionSpecificationLoadAsync,
} from "hooks/services/useDestinationHook";
import { Connection } from "core/resources/Connection";
import { ConnectionConfiguration } from "core/domain/connection";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

import { createFormErrorMessage } from "utils/errorStatusMessage";
import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { Connector, Destination } from "core/domain/connector";

const Content = styled.div`
  width: 100%;
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
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(
    null
  );

  const destinationSpecification = useDestinationDefinitionSpecificationLoadAsync(
    currentDestination.destinationDefinitionId
  );

  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId,
    }
  );

  const {
    updateDestination,
    deleteDestination,
    checkDestinationConnection,
  } = useDestination();

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setErrorStatusRequest(null);
    try {
      await updateDestination({
        values,
        destinationId: currentDestination.destinationId,
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
      await checkDestinationConnection({
        values,
        destinationId: currentDestination.destinationId,
      });
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  const onDelete = () =>
    deleteDestination({
      connectionsWithDestination,
      destination: currentDestination,
    });

  return (
    <Content>
      <ConnectorCard
        onRetest={onRetest}
        isEditMode
        onSubmit={onSubmitForm}
        formType="destination"
        availableServices={[destinationDefinition]}
        formValues={{
          ...currentDestination,
          serviceType: Connector.id(destinationDefinition),
        }}
        selectedConnector={destinationSpecification}
        successMessage={saved && <FormattedMessage id="form.changesSaved" />}
        errorMessage={
          errorStatusRequest && createFormErrorMessage(errorStatusRequest)
        }
        title={<FormattedMessage id="destination.destinationSettings" />}
        jobInfo={LogsRequestError.extractJobInfo(errorStatusRequest)}
      />
      <DeleteBlock type="destination" onDelete={onDelete} />
    </Content>
  );
};

export default DestinationsSettings;

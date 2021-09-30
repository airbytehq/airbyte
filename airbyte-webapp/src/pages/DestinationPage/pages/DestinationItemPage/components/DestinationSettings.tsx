import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ContentCard from "components/ContentCard";
import ServiceForm from "views/Connector/ServiceForm";
import { Destination } from "core/resources/Destination";
import DestinationDefinitionSpecificationResource from "core/resources/DestinationDefinitionSpecification";
import useDestination from "hooks/services/useDestinationHook";
import DeleteBlock from "components/DeleteBlock";
import { Connection } from "core/resources/Connection";
import { JobInfo } from "core/resources/Scheduler";
import { JobsLogItem } from "components/JobItem";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectionConfiguration } from "core/domain/connection";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

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
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    statusMessage: string | React.ReactNode;
    response: JobInfo;
  } | null>(null);

  const destinationSpecification = useResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId,
    }
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
      const errorStatusMessage = createFormErrorMessage(e);

      setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage });
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
      const errorStatusMessage = createFormErrorMessage(e);

      setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage });
    }
  };

  const onDelete = async () => {
    await deleteDestination({
      connectionsWithDestination,
      destination: currentDestination,
    });
  };

  return (
    <Content>
      <ContentCard
        title={<FormattedMessage id="destination.destinationSettings" />}
      >
        <ServiceForm
          onRetest={onRetest}
          isEditMode
          onSubmit={onSubmitForm}
          formType="destination"
          availableServices={[destinationDefinition]}
          formValues={{
            ...currentDestination,
            serviceType: currentDestination.destinationDefinitionId,
          }}
          specifications={destinationSpecification.connectionSpecification}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          errorMessage={errorStatusRequest?.statusMessage}
        />
        <JobsLogItem jobInfo={errorStatusRequest?.response} />
      </ContentCard>
      <DeleteBlock type="destination" onDelete={onDelete} />
    </Content>
  );
};

export default DestinationsSettings;

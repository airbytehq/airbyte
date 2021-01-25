import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { Destination } from "../../../../../core/resources/Destination";
import DestinationDefinitionSpecificationResource from "../../../../../core/resources/DestinationDefinitionSpecification";
import useDestination from "../../../../../components/hooks/services/useDestinationHook";
import DeleteBlock from "../../../../../components/DeleteBlock";
import { Connection } from "../../../../../core/resources/Connection";
import { JobInfo } from "../../../../../core/resources/Scheduler";
import { JobsLogItem } from "../../../../../components/JobItem";
import { createFormErrorMessage } from "../../../../../utils/errorStatusMessage";

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
  connectionsWithDestination
}) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    statusMessage: string | React.ReactNode;
    response: JobInfo;
  } | null>(null);

  const destinationSpecification = useResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId
    }
  );

  const { updateDestination, deleteDestination } = useDestination();

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(null);
    try {
      await updateDestination({
        values,
        destinationId: currentDestination.destinationId,
        destinationDefinitionId: currentDestination.destinationDefinitionId
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
      destination: currentDestination
    });
  };

  return (
    <Content>
      <ContentCard
        title={<FormattedMessage id="destination.destinationSettings" />}
      >
        <ServiceForm
          isEditMode
          onSubmit={onSubmitForm}
          formType="destination"
          dropDownData={[
            {
              value: currentDestination.destinationDefinitionId,
              text: currentDestination.destinationName,
              img: "/default-logo-catalog.svg"
            }
          ]}
          formValues={{
            ...currentDestination,
            serviceType: currentDestination.destinationDefinitionId
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

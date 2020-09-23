import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource, useFetcher } from "rest-hooks";

import PageTitle from "../../components/PageTitle";
import ContentCard from "../../components/ContentCard";
import ServiceForm from "../../components/ServiceForm";
import DestinationImplementationResource from "../../core/resources/DestinationImplementation";
import config from "../../config";
import DestinationSpecificationResource from "../../core/resources/DestinationSpecification";
import DestinationResource from "../../core/resources/Destination";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 19px auto;
`;

const DestinationPage: React.FC = () => {
  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const destinationSpecification = useResource(
    DestinationSpecificationResource.detailShape(),
    {
      destinationId: currentDestination.destinationId
    }
  );
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
  });
  const updateDestination = useFetcher(
    DestinationImplementationResource.updateShape()
  );

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    setErrorMessage("");
    const result = await updateDestination(
      {
        destinationImplementationId:
          currentDestination.destinationImplementationId
      },
      {
        name: values.name,
        destinationImplementationId:
          currentDestination.destinationImplementationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );

    if (result.status === "failure") {
      setErrorMessage(result.message);
    } else {
      setSaved(true);
    }
  };

  return (
    <>
      <PageTitle
        title={<FormattedMessage id="sidebar.destination" />}
        withLine
      />
      <Content>
        <ContentCard
          title={<FormattedMessage id="destination.destinationSettings" />}
        >
          <ServiceForm
            onSubmit={onSubmitForm}
            formType="destination"
            dropDownData={[
              {
                value: destination.destinationId,
                text: destination.name,
                img: "/default-logo-catalog.svg"
              }
            ]}
            formValues={{
              ...currentDestination.connectionConfiguration,
              name: currentDestination.name,
              serviceType: destination.destinationId
            }}
            specifications={destinationSpecification.connectionSpecification}
            successMessage={
              saved && <FormattedMessage id="form.changesSaved" />
            }
            errorMessage={errorMessage}
          />
        </ContentCard>
      </Content>
    </>
  );
};

export default DestinationPage;

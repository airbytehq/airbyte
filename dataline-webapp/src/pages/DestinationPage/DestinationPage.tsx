import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource, useFetcher } from "rest-hooks";

import PageTitle from "../../components/PageTitle";
import ContentCard from "../../components/ContentCard";
import ServiceForm from "../../components/ServiceForm";
import DestinationImplementationResource from "../../core/resources/DestinationImplementation";
import config from "../../config";
import DestinationSpecificationResource from "../../core/resources/DestinationSpecification";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 19px auto;
`;

const DestinationPage: React.FC = () => {
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
      // destinationSpecificationId: currentDestination.destinationSpecificationId
      // destinationId: currentDestination.destinationId
      destinationId: "22f6c74f-5699-40ff-833c-4a879ea40133" // TODO: fix it. Take from API
    }
  );
  const updateDestination = useFetcher(
    DestinationImplementationResource.updateShape()
  );

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    await updateDestination(
      {},
      {
        destinationImplementationId:
          currentDestination.destinationImplementationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );
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
            formType="source"
            dropDownData={[
              {
                value: "Test",
                text: "Test",
                img: "/default-logo-catalog.svg"
              }
            ]}
            formValues={{
              ...currentDestination.connectionConfiguration,
              name: "Test",
              serviceType: "Test"
            }}
            specifications={destinationSpecification.connectionSpecification}
          />
        </ContentCard>
      </Content>
    </>
  );
};

export default DestinationPage;

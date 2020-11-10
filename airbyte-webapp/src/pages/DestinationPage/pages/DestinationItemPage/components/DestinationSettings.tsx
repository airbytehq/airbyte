import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { Destination } from "../../../../../core/resources/Destination";
import DestinationDefinitionSpecificationResource from "../../../../../core/resources/DestinationDefinitionSpecification";
import useDestination from "../../../../../components/hooks/services/useDestinationHook";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 19px auto;
`;

type IProps = {
  currentDestination: Destination;
};

const DestinationsSettings: React.FC<IProps> = ({ currentDestination }) => {
  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const destinationSpecification = useResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId
    }
  );

  const { updateDestination } = useDestination();

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    setErrorMessage("");
    const result = await updateDestination({
      values,
      destinationId: currentDestination.destinationId
    });

    if (result.status === "failure") {
      setErrorMessage(result.message);
    } else {
      setSaved(true);
    }
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
              text: currentDestination.name,
              img: "/default-logo-catalog.svg"
            }
          ]}
          formValues={{
            ...currentDestination,
            serviceType: currentDestination.destinationDefinitionId
          }}
          specifications={destinationSpecification.connectionSpecification}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          errorMessage={errorMessage}
        />
      </ContentCard>
    </Content>
  );
};

export default DestinationsSettings;

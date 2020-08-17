import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import PageTitle from "../../components/PageTitle";
import ContentCard from "../../components/ContentCard";
import ServiceForm from "../../components/ServiceForm";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 19px auto;
`;

const DestinationPage: React.FC = () => {
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
            onSubmit={() => null}
            formType="source"
            dropDownData={[
              { value: "Test", text: "Test", img: "/default-logo-catalog.svg" }
            ]}
            formValues={{ name: "Test", serviceType: "Test" }}
          />
        </ContentCard>
      </Content>
    </>
  );
};

export default DestinationPage;

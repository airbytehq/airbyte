import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import DeleteSource from "./DeleteSource";
import ServiceForm from "../../../../../components/ServiceForm";

type IProps = {
  sourceData: any;
};

const Content = styled.div`
  max-width: 639px;
  margin: 18px auto;
`;

const SettingsView: React.FC<IProps> = ({ sourceData }) => {
  return (
    <Content>
      <ContentCard title={<FormattedMessage id={"sources.sourceSettings"} />}>
        <ServiceForm
          onSubmit={() => null}
          formType="connection"
          dropDownData={[
            {
              value: sourceData.source,
              text: sourceData.source,
              img: "/default-logo-catalog.svg"
            }
          ]}
          formValues={{
            name: sourceData.name,
            serviceType: sourceData.source,
            frequency: sourceData.frequency
          }}
        />
      </ContentCard>
      <DeleteSource />
    </Content>
  );
};

export default SettingsView;

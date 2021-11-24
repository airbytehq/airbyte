import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";

type TransformationViewProps = {};

const Content = styled.div`
  max-width: 1073px;
  margin: 18px auto;
  padding-bottom: 10px;
`;

const Card = styled(ContentCard)`
  margin-bottom: 10px;
`;

const TransformationView: React.FC<TransformationViewProps> = () => {
  return (
    <Content>
      <Card title={<FormattedMessage id="connection.normalization" />} />
      <ContentCard
        title={<FormattedMessage id="connection.customTransformations" />}
      />
    </Content>
  );
};

export default TransformationView;

import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BaseClearView from "components/BaseClearView";
import { H4 } from "components/Titles";

const Content = styled(ContentCard)`
  width: 100%;
  max-width: 600px;
  padding: 50px 15px;
`;

const ServerIsStarting: React.FC = () => {
  return (
    <BaseClearView>
      <Content>
        <H4 center>
          <FormattedMessage id="webapp.cannotReachServer" />
        </H4>
      </Content>
    </BaseClearView>
  );
};

export default ServerIsStarting;

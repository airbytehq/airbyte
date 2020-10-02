import React from "react";
import styled from "styled-components";

import ContentCard from "../../ContentCard";
import BaseClearView from "../../BaseClearView";
import { H4 } from "../../Titles";
import { FormattedMessage } from "react-intl";

const Content = styled(ContentCard)`
  width: 100%;
  max-width: 600px;
  padding: 50px 0;
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

import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { H1, H3 } from "components";
import WorkspacesList from "./components/WorkspacesList";

const MainContent = styled.div`
  width: 100%;
  max-width: 680px;
  height: 100%;
  padding: 26px;
  margin: 0 auto;
  text-align: center;
`;

const Logo = styled.img`
  margin-bottom: 58px;
`;

const Subtitle = styled(H3)`
  margin: 17px 0 33px;
  line-height: 32px;
`;

const WorkspacesPage: React.FC = () => {
  return (
    <MainContent>
      <Logo src="/cloud-main-logo.svg" width={186} />
      <H1 center bold>
        <FormattedMessage id="workspaces.title" />
      </H1>
      <Subtitle center>
        <FormattedMessage id="workspaces.subtitle" />
      </Subtitle>
      <WorkspacesList />
    </MainContent>
  );
};

export default WorkspacesPage;

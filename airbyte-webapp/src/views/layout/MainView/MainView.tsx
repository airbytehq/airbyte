import React from "react";
import styled from "styled-components";

import { LoadingPage } from "components";
import SideBar from "views/layout/SideBar";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";

const MainContainer = styled.div`
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  min-height: 680px;
`;

const Content = styled.div`
  overflow-y: auto;
  width: 100%;
  height: 100%;
`;

const MainView: React.FC = (props) => (
  <MainContainer>
    <SideBar />
    <Content>
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
        <React.Suspense fallback={<LoadingPage />}>
          {props.children}
        </React.Suspense>
      </ResourceNotFoundErrorBoundary>
    </Content>
  </MainContainer>
);

export default MainView;

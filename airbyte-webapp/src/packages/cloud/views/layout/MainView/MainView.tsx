import React from "react";
import styled from "styled-components";
import { Outlet } from "react-router-dom";

import { LoadingPage } from "components";

import SideBar from "packages/cloud/views/layout/SideBar";
import { ErrorBoundary } from "./ErrorBoundary";
import { NotFoundView } from "views/common/StartOverErrorView";
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

const MainView: React.FC = ({ children }) => (
  <MainContainer>
    <ErrorBoundary errorComponent={<NotFoundView />}>
      <SideBar />
      <Content>
        <ResourceNotFoundErrorBoundary errorComponent={<NotFoundView />}>
          <React.Suspense fallback={LoadingPage}>
            {children ?? <Outlet />}
          </React.Suspense>
        </ResourceNotFoundErrorBoundary>
      </Content>
    </ErrorBoundary>
  </MainContainer>
);

export default MainView;

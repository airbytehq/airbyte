import React, { Suspense } from "react";
import styled from "styled-components";

import SideBar from "views/layout/SideBar";
import LoadingPage from "components/LoadingPage";

const MainContainer = styled.div`
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: row;
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
      <Suspense fallback={<LoadingPage />}>{props.children}</Suspense>
    </Content>
  </MainContainer>
);

export default MainView;

import React from "react";
import styled from "styled-components";
import SideBar from "packages/cloud/views/layout/SideBar";

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
    <Content>{props.children}</Content>
  </MainContainer>
);

export default MainView;

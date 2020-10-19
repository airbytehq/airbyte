import React from "react";
import styled from "styled-components";

const Content = styled.div`
  overflow-y: auto;
  height: calc(100% - 67px);
  margin-top: -17px;
  padding-top: 17px;
`;

const Page = styled.div`
  overflow-y: hidden;
  height: 100%;
`;

type IProps = {
  title?: React.ReactNode;
  children?: React.ReactNode;
};

const MainPageWithScroll: React.FC<IProps> = ({ title, children }) => {
  return (
    <Page>
      {title}
      <Content>{children}</Content>
    </Page>
  );
};

export default MainPageWithScroll;

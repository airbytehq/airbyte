import React from "react";
import styled from "styled-components";

const Content = styled.div`
  overflow-y: auto;
  padding-top: 17px;
  height: 100%;
`;

const Page = styled.div`
  overflow-y: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

/**
 * @param headTitle the title shown in the browser toolbar
 * @param pageTitle the title shown on the page
 */
type IProps = {
  headTitle?: React.ReactNode;
  pageTitle?: React.ReactNode;
  children?: React.ReactNode;
};

const MainPageWithScroll: React.FC<IProps> = ({
  headTitle,
  pageTitle,
  children,
}) => {
  return (
    <Page>
      {headTitle}
      {pageTitle}
      <Content>{children}</Content>
    </Page>
  );
};

export default MainPageWithScroll;

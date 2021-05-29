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

import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import LoadingPage from "components/LoadingPage";
import AccountSettings from "./components/AccountSettings";

const Content = styled.div`
  margin: 0 33px 0 27px;
  height: 100%;
`;

const SettingsPage: React.FC = () => {
  return (
    <MainPageWithScroll
      title={
        <PageTitle
          withLine
          title={<FormattedMessage id="sidebar.settings" />}
        />
      }
    >
      <Content>
        <Suspense fallback={<LoadingPage />}>
          <AccountSettings />
        </Suspense>
      </Content>
    </MainPageWithScroll>
  );
};

export default SettingsPage;

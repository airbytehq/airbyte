import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router";

import useConnector from "components/hooks/services/useConnector";
import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import LoadingPage from "components/LoadingPage";
import HeadTitle from "components/HeadTitle";
import SideMenu from "components/SideMenu";
import { Routes } from "pages/routes";
import useRouter from "components/hooks/useRouterHook";
import NotificationPage from "./pages/NotificationPage";
import ConfigurationsPage from "./pages/ConfigurationsPage";
import MetricsPage from "./pages/MetricsPage";
import AccountPage from "./pages/AccountPage";
import { DestinationsPage, SourcesPage } from "./pages/ConnectorsPage";

const Content = styled.div`
  margin: 0 33px 0 27px;
  height: 100%;
  display: flex;
  flex-direction: row;
`;
const MainView = styled.div`
  width: 100%;
  margin-left: 47px;
`;

const SettingsPage: React.FC = () => {
  const { push, pathname } = useRouter();
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const menuItems = [
    {
      id: `${Routes.Settings}${Routes.Account}`,
      name: <FormattedMessage id="settings.account" />,
    },
    {
      id: `${Routes.Settings}${Routes.Source}`,
      name: <FormattedMessage id="tables.sources" />,
      indicatorCount: countNewSourceVersion,
    },
    {
      id: `${Routes.Settings}${Routes.Destination}`,
      name: <FormattedMessage id="tables.destinations" />,
      indicatorCount: countNewDestinationVersion,
    },
    {
      id: `${Routes.Settings}${Routes.Configuration}`,
      name: <FormattedMessage id="admin.configuration" />,
    },
    {
      id: `${Routes.Settings}${Routes.Notifications}`,
      name: <FormattedMessage id="settings.notifications" />,
    },
    {
      id: `${Routes.Settings}${Routes.Metrics}`,
      name: <FormattedMessage id="settings.metrics" />,
    },
  ];

  const onSelectMenuItem = (newPath: string) => push(newPath);

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.settings" }]} />}
      pageTitle={
        <PageTitle
          withLine
          title={<FormattedMessage id="sidebar.settings" />}
        />
      }
    >
      <Content>
        <SideMenu
          data={menuItems}
          onSelect={onSelectMenuItem}
          activeItem={pathname}
        />

        <MainView>
          <Suspense fallback={<LoadingPage />}>
            <Switch>
              <Route path={`${Routes.Settings}${Routes.Account}`}>
                <AccountPage />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Source}`}>
                <SourcesPage />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Destination}`}>
                <DestinationsPage />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Configuration}`}>
                <ConfigurationsPage />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Notifications}`}>
                <NotificationPage />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Metrics}`}>
                <MetricsPage />
              </Route>

              <Redirect to={`${Routes.Settings}${Routes.Account}`} />
            </Switch>
          </Suspense>
        </MainView>
      </Content>
    </MainPageWithScroll>
  );
};

export default SettingsPage;

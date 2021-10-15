import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router";

import useConnector from "hooks/services/useConnector";
import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import LoadingPage from "components/LoadingPage";
import HeadTitle from "components/HeadTitle";
import SideMenu from "components/SideMenu";
import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import NotificationPage from "./pages/NotificationPage";
import ConfigurationsPage from "./pages/ConfigurationsPage";
import MetricsPage from "./pages/MetricsPage";
import AccountPage from "./pages/AccountPage";
import { DestinationsPage, SourcesPage } from "./pages/ConnectorsPage";
import { CategoryItem } from "components/SideMenu/SideMenu";

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

export type PageConfig = {
  menuConfig: CategoryItem[];
};

type SettingsPageProps = {
  pageConfig?: PageConfig;
};

const SettingsPage: React.FC<SettingsPageProps> = ({ pageConfig }) => {
  const { push, pathname } = useRouter();
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const menuItems: CategoryItem[] = pageConfig?.menuConfig || [
    {
      routes: [
        {
          path: `${Routes.Settings}${Routes.Account}`,
          name: <FormattedMessage id="settings.account" />,
          component: AccountPage,
        },
        {
          path: `${Routes.Settings}${Routes.Source}`,
          name: <FormattedMessage id="tables.sources" />,
          indicatorCount: countNewSourceVersion,
          component: SourcesPage,
        },
        {
          path: `${Routes.Settings}${Routes.Destination}`,
          name: <FormattedMessage id="tables.destinations" />,
          indicatorCount: countNewDestinationVersion,
          component: DestinationsPage,
        },
        {
          path: `${Routes.Settings}${Routes.Configuration}`,
          name: <FormattedMessage id="admin.configuration" />,
          component: ConfigurationsPage,
        },
        {
          path: `${Routes.Settings}${Routes.Notifications}`,
          name: <FormattedMessage id="settings.notifications" />,
          component: NotificationPage,
        },
        {
          path: `${Routes.Settings}${Routes.Metrics}`,
          name: <FormattedMessage id="settings.metrics" />,
          component: MetricsPage,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => push(newPath);
  const firstRoute = menuItems?.[0].routes?.[0]?.path;

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.settings" }]} />}
      pageTitle={
        <PageTitle title={<FormattedMessage id="sidebar.settings" />} />
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
              {menuItems.flatMap((menuItem) =>
                menuItem.routes.map((route) => (
                  <Route
                    key={`${route.path}`}
                    path={`${route.path}`}
                    component={route.component}
                  />
                ))
              )}

              <Redirect
                to={
                  firstRoute
                    ? `${menuItems?.[0].routes?.[0]?.path}`
                    : Routes.Root
                }
              />
            </Switch>
          </Suspense>
        </MainView>
      </Content>
    </MainPageWithScroll>
  );
};

export default SettingsPage;

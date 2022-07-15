import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import SideMenu from "components/SideMenu";
import { CategoryItem } from "components/SideMenu/SideMenu";

import useConnector from "hooks/services/useConnector";
import useRouter from "hooks/useRouter";

import AccountPage from "./pages/AccountPage";
import ConfigurationsPage from "./pages/ConfigurationsPage";
import { DestinationsPage, SourcesPage } from "./pages/ConnectorsPage";
import MetricsPage from "./pages/MetricsPage";
import NotificationPage from "./pages/NotificationPage";

const Content = styled.div`
  margin: 0 33px 0 27px;
  display: flex;
  flex-direction: row;
  padding-bottom: 15px;
`;
const MainView = styled.div`
  width: 100%;
  margin-left: 47px;
`;

export interface PageConfig {
  menuConfig: CategoryItem[];
}

interface SettingsPageProps {
  pageConfig?: PageConfig;
}

export const SettingsRoute = {
  Account: "account",
  Destination: "destination",
  Source: "source",
  Configuration: "configuration",
  Notifications: "notifications",
  Metrics: "metrics",
} as const;

const SettingsPage: React.FC<SettingsPageProps> = ({ pageConfig }) => {
  const { push, pathname } = useRouter();
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const menuItems: CategoryItem[] = pageConfig?.menuConfig || [
    {
      routes: [
        {
          path: `${SettingsRoute.Account}`,
          name: <FormattedMessage id="settings.account" />,
          component: AccountPage,
        },
        {
          path: `${SettingsRoute.Source}`,
          name: <FormattedMessage id="tables.sources" />,
          indicatorCount: countNewSourceVersion,
          component: SourcesPage,
        },
        {
          path: `${SettingsRoute.Destination}`,
          name: <FormattedMessage id="tables.destinations" />,
          indicatorCount: countNewDestinationVersion,
          component: DestinationsPage,
        },
        {
          path: `${SettingsRoute.Configuration}`,
          name: <FormattedMessage id="admin.configuration" />,
          component: ConfigurationsPage,
        },
        {
          path: `${SettingsRoute.Notifications}`,
          name: <FormattedMessage id="settings.notifications" />,
          component: NotificationPage,
        },
        {
          path: `${SettingsRoute.Metrics}`,
          name: <FormattedMessage id="settings.metrics" />,
          component: MetricsPage,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => push(newPath);
  const firstRoute = menuItems[0].routes?.[0]?.path;

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.settings" }]} />}
      pageTitle={<PageTitle title={<FormattedMessage id="sidebar.settings" />} />}
    >
      <Content>
        <SideMenu data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} />

        <MainView>
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              {menuItems
                .flatMap((menuItem) => menuItem.routes)
                .map(({ path, component: Component }) => (
                  <Route key={path} path={path} element={<Component />} />
                ))}

              <Route path="*" element={<Navigate to={firstRoute} replace />} />
            </Routes>
          </Suspense>
        </MainView>
      </Content>
    </MainPageWithScroll>
  );
};

export default SettingsPage;

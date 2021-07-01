import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router";

import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import LoadingPage from "components/LoadingPage";
import AccountSettings from "./components/AccountSettings";
import HeadTitle from "components/HeadTitle";
import SideMenu from "components/SideMenu";
import { Routes } from "pages/routes";
import useRouter from "../../components/hooks/useRouterHook";

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

  const menuItems = [
    {
      id: `${Routes.Settings}${Routes.Source}`,
      name: <FormattedMessage id="tables.sources" />,
    },
    {
      id: `${Routes.Settings}${Routes.Destination}`,
      name: <FormattedMessage id="tables.destinations" />,
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
              <Route path={`${Routes.Settings}${Routes.Source}`}>
                <div>Source</div>
              </Route>
              <Route path={`${Routes.Settings}${Routes.Destination}`}>
                <div>Destination</div>
              </Route>
              <Route path={`${Routes.Settings}${Routes.Configuration}`}>
                <div>Configuration</div>
              </Route>
              <Route path={`${Routes.Settings}${Routes.Notifications}`}>
                <AccountSettings />
              </Route>
              <Route path={`${Routes.Settings}${Routes.Metrics}`}>
                <div>Metrics</div>
              </Route>

              <Redirect to={`${Routes.Settings}${Routes.Source}`} />
            </Switch>
          </Suspense>
        </MainView>
      </Content>
    </MainPageWithScroll>
  );
};

export default SettingsPage;

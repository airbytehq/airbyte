import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import MessageBox from "components/base/MessageBox";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import { TabMenu, CategoryItem } from "components/TabMenu";

import { useUser } from "core/AuthContext";
import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import useRouter from "hooks/useRouter";

import AccountSettingsPage from "./pages/AccountSettingsPage";
import NotificationPage from "./pages/NotificationPage";
import PlansBillingPage from "./pages/PlansBillingPage";
import UserManagementPage from "./pages/UserManagementPage";

const PageContainer = styled.div`
  width: 100%;
  height: auto;
  display: flex;
  flex-direction: row;
`;

const Seperator = styled.div`
  width: 10px;
  background: transparent;
  height: 100%;
`;

const ContentContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  background-color: white;
  padding: 16px 26px 26px 26px;
`;

const PageHeaderContainer = styled.div`
  width: 100%;
  position: relative;
`;

const TabContainer = styled.div`
  margin: 20px 0 40px 0;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainView = styled.div`
  width: 100%;
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
  UserManagement: "user-management",
  AccountSettings: "account-settings",
  PlanAndBilling: "plan-and-billing",
} as const;

const SettingsPage: React.FC<SettingsPageProps> = ({ pageConfig }) => {
  const { push, pathname } = useRouter();
  const { user } = useUser();

  const [messageId, setMessageId] = useState<string>("");
  const [messageType, setMessageType] = useState<"info" | "error">("info");

  const menuItems: CategoryItem[] = pageConfig?.menuConfig || [
    {
      routes: [
        {
          path: `${SettingsRoute.UserManagement}`,
          name: <FormattedMessage id="settings.user.management" />,
          component: <UserManagementPage setMessageId={setMessageId} setMessageType={setMessageType} />,
          show:
            getRoleAgainstRoleNumber(user.role) === ROLES.Administrator_Owner ||
            getRoleAgainstRoleNumber(user.role) === ROLES.Administrator
              ? true
              : false,
        },
        {
          path: `${SettingsRoute.AccountSettings}`,
          name: <FormattedMessage id="settings.account.settings" />,
          component: <AccountSettingsPage />,
          show: true,
        },
        {
          path: `${SettingsRoute.PlanAndBilling}`,
          name: <FormattedMessage id="settings.plan.billing" />,
          component: <PlansBillingPage setMessageId={setMessageId} setMessageType={setMessageType} />,
          show:
            getRoleAgainstRoleNumber(user.role) === ROLES.Administrator_Owner ||
            getRoleAgainstRoleNumber(user.role) === ROLES.Administrator
              ? true
              : false,
        },
        {
          path: `${SettingsRoute.Notifications}`,
          name: <FormattedMessage id="settings.notificationSettings" />,
          component: <NotificationPage />,
          show: true,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => push(newPath);
  const firstRoute = (): string => {
    const { routes } = menuItems[0];
    const filteredRoutes = routes.filter((route) => route.show === true);
    if (filteredRoutes.length > 0) {
      return filteredRoutes[0]?.path;
    }
    return "";
  };

  return (
    <PageContainer>
      <Seperator />
      <ContentContainer>
        <MessageBox message={messageId} onClose={() => setMessageId("")} type={messageType} />
        <MainPageWithScroll
          withPadding
          headTitle={<HeadTitle titles={[{ id: "sidebar.settings" }]} />}
          pageTitle={
            <PageHeaderContainer>
              <div style={{ padding: "24px 0 0 20px" }}>
                <PageTitle title={<FormattedMessage id="sidebar.settings" />} />
              </div>
            </PageHeaderContainer>
          }
        >
          <Content>
            <TabContainer>
              <TabMenu data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} />
            </TabContainer>
            <MainView>
              <Suspense fallback={<LoadingPage />}>
                <Routes>
                  {menuItems
                    .flatMap((menuItem) => menuItem.routes)
                    .map(
                      ({ path, component: Component, show }) =>
                        show && <Route key={path} path={`${path}/*`} element={Component} />
                    )}
                  <Route path="*" element={<Navigate to={firstRoute()} replace />} />
                </Routes>
              </Suspense>
            </MainView>
          </Content>
        </MainPageWithScroll>
      </ContentContainer>
    </PageContainer>
  );
};

export default SettingsPage;

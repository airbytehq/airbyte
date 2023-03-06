import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import LoadingPage from "components/LoadingPage";
import { SideMenuItem } from "components/TabMenu";

import useRouter from "hooks/useRouter";

import { Sidebar } from "./components";
// import AccountPage from "./pages/AccountPage";
// import PasswordPage from "./pages/PasswordPage";

import LanguagePage from "./pages/LanguagePage";
import NotificationPage from "./pages/NotificationPage";

const Container = styled.div`
  width: 100%;
  height: 100%;
  border: 1px solid #eff0f5;
  border-radius: 6px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
`;

const ContentContainer = styled.div`
  padding: 20px 30px;
  width: 100%;
`;

export const AccountSettingsRoute = {
  Account: "account",
  Language: "language",
  Notifications: "notifications",
  Password: "password",
} as const;

const AccountSettingsPage: React.FC = () => {
  const { push } = useRouter();

  const menuItems: SideMenuItem[] = [
    {
      path: `${AccountSettingsRoute.Language}`,
      name: <FormattedMessage id="settings.accountSetting.language" />,
      component: <LanguagePage />,
    },
    {
      path: `${AccountSettingsRoute.Notifications}`,
      name: <FormattedMessage id="settings.accountSetting.notifications" />,
      component: <NotificationPage />,
    },
    // {
    //   path: `${AccountSettingsRoute.Account}`,
    //   name: <FormattedMessage id="settings.accountSetting.account" />,
    //   component: <AccountPage />
    // },
    // {
    //   path: `${AccountSettingsRoute.Password}`,
    //   name: <FormattedMessage id="settings.accountSetting.password" />,
    //   component: <PasswordPage />
    // }
  ];

  const onSelectItem = (path: string) => push(path);

  return (
    <Container>
      <Sidebar menuItems={menuItems} onSelectItem={onSelectItem} />
      <ContentContainer>
        <Suspense fallback={<LoadingPage />}>
          <Routes>
            {menuItems.map(({ path, component: Component }) => (
              <Route key={path} path={path} element={Component} />
            ))}
            <Route path="*" element={<Navigate to={`${menuItems[0].path}`} replace />} />
          </Routes>
        </Suspense>
      </ContentContainer>
    </Container>
  );
};

export default AccountSettingsPage;

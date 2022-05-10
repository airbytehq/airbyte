import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import { PageTitle } from "components";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import SideMenu from "components/SideMenu";
import { CategoryItem } from "components/SideMenu/SideMenu";

import useRouter from "hooks/useRouter";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CreditsUsagePage from "./components/CreditsUsagePage";
import { EmailVerificationHint } from "./components/EmailVerificationHint";
import RemainingCredits from "./components/RemainingCredits";

const Content = styled.div`
  margin: 0 33px 0 27px;
  height: 100%;
`;

const MainInfo = styled.div`
  display: flex;
  flex-direction: row;
  margin-top: 29px;
`;

const MainView = styled.div`
  width: 100%;
  margin-left: 47px;
`;

const EmailVerificationHintWithMargin = styled(EmailVerificationHint)`
  margin-bottom: 8px;
`;

const CreditsPage: React.FC = () => {
  const { push, pathname } = useRouter();
  const onSelectMenuItem = (newPath: string) => push(newPath);
  const { emailVerified } = useAuthService();

  const menuItems: CategoryItem[] = [
    {
      routes: [
        {
          path: ``,
          name: <FormattedMessage id="credits.creditUsage" />,
          component: CreditsUsagePage,
        },
      ],
    },
  ];

  const firstRoute = menuItems?.[0].routes?.[0]?.path;

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "credits.credits" }]} />}
      pageTitle={<PageTitle title={<FormattedMessage id="credits.credits" />} />}
    >
      <Content>
        {!emailVerified && <EmailVerificationHintWithMargin />}
        <RemainingCredits selfServiceCheckoutEnabled={emailVerified} />
        <MainInfo>
          <SideMenu data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} />
          <MainView>
            <Suspense fallback={<LoadingPage />}>
              <Routes>
                {menuItems.flatMap((menuItem) =>
                  menuItem.routes.map(({ path, component: Component }) => (
                    <Route key={`${path}`} path={`${path}`} element={<Component />} />
                  ))
                )}

                <Route
                  path="*"
                  element={<Navigate to={firstRoute ? `${menuItems?.[0].routes?.[0]?.path}` : CloudRoutes.Root} />}
                />
              </Routes>
            </Suspense>
          </MainView>
        </MainInfo>
      </Content>
    </MainPageWithScroll>
  );
};

export default CreditsPage;

import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router";

import HeadTitle from "components/HeadTitle";
import MainPageWithScroll from "components/MainPageWithScroll";
import SideMenu from "components/SideMenu";
import LoadingPage from "components/LoadingPage";
import { CategoryItem } from "components/SideMenu/SideMenu";
import { Routes } from "packages/cloud/routes";
import useRouter from "hooks/useRouter";
import CreditsTitle from "./components/CreditsTitle";
import RemainingCredits from "./components/RemainingCredits";
import CreditsUsagePage from "./components/CreditsUsagePage";

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

const CreditsPage: React.FC = () => {
  const { push, pathname } = useRouter();
  const onSelectMenuItem = (newPath: string) => push(newPath);

  const menuItems: CategoryItem[] = [
    {
      routes: [
        {
          path: `${Routes.Credits}`,
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
      pageTitle={<CreditsTitle />}
    >
      <Content>
        <RemainingCredits />
        <MainInfo>
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
        </MainInfo>
      </Content>
    </MainPageWithScroll>
  );
};

export default CreditsPage;

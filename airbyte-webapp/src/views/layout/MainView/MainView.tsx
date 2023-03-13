import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { theme } from "theme";

import { LoadingPage } from "components";
import { CreateStepTypes } from "components/ConnectionStep";

import useRouter from "hooks/useRouter";
import { UpgradePlanBar } from "pages/ConnectionPage/pages/AllConnectionsPage/components/UpgradePlanBar";
import { RoutePaths } from "pages/routePaths";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import SideBar from "views/layout/SideBar";

const MainContainer = styled.div`
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  min-height: 680px;
`;

const Content = styled.div<{
  backgroundColor?: string;
}>`
  background: ${({ backgroundColor }) => backgroundColor};
  overflow-y: auto;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const hasCurrentStep = (state: unknown): state is { currentStep: string } => {
  return (
    typeof state === "object" && state !== null && typeof (state as { currentStep?: string }).currentStep === "string"
  );
};

const MainView: React.FC = (props) => {
  const { pathname, location } = useRouter();
  const [isSidebar, setIsSidebar] = useState<boolean>(true);
  const [backgroundColor, setBackgroundColor] = useState<string>(theme.backgroundColor);

  const hasSidebarRoutes: string[] = [
    RoutePaths.Source,
    RoutePaths.SelectSource,
    RoutePaths.Connections,
    RoutePaths.Status,
    RoutePaths.SelectConnection,
    RoutePaths.Destination,
    RoutePaths.SelectDestination,
    RoutePaths.UserManagement,
    RoutePaths.AccountSettings,
    RoutePaths.PlanAndBilling,
    RoutePaths.Notifications,
    RoutePaths.Configurations,
    RoutePaths.Language,
  ];

  // TODO: not the proper solution but works for now
  // const isSidebar =
  //   !pathname.split("/").includes(RoutePaths.Payment) && !pathname.split("/").includes(RoutePaths.PaymentError);

  useEffect(() => {
    const pathnames = pathname.split("/");
    const lastPathName = pathnames[pathnames.length - 1];
    let isSidebarBol = false;

    // connection has sidebar but source/destination no
    if (lastPathName === RoutePaths.DangerZone) {
      isSidebarBol = pathnames.includes(RoutePaths.Connections);
    } else {
      isSidebarBol = hasSidebarRoutes.includes(lastPathName);
    }

    // The configuration step background color in Add Connection is #F8F8FE , and the page color of the previous steps is white.
    if (lastPathName === RoutePaths.ConnectionNew) {
      if (hasCurrentStep(location.state) && location.state.currentStep === CreateStepTypes.CREATE_CONNECTION) {
        setBackgroundColor("#F8F8FE");
        isSidebarBol = false;
      } else {
        setBackgroundColor(theme.white);
      }
    } else if (lastPathName === RoutePaths.Payment) {
      setBackgroundColor(theme.backgroundColor);
    } else if (isSidebarBol) {
      // In the page with sidebar, the background color of these three pages is #F8F8FE, and the others are the theme background color.
      if (
        lastPathName === RoutePaths.SelectSource ||
        lastPathName === RoutePaths.SelectDestination ||
        lastPathName === RoutePaths.SelectConnection
      ) {
        setBackgroundColor("#F8F8FE");
      }
      // else if(
      //   lastPathName === RoutePaths.AccountSettings ||
      //   lastPathName === RoutePaths.Language ||
      //   lastPathName === RoutePaths.Notifications  ||
      //   lastPathName === RoutePaths.PlanAndBilling
      // ) {
      //   setBackgroundColor(theme.white);
      // }
      else {
        setBackgroundColor(theme.backgroundColor);
      }
    } else {
      // Other page background color is white.
      setBackgroundColor(theme.white);
    }
    setIsSidebar(isSidebarBol);
  }, [pathname, hasSidebarRoutes]);

  return (
    <MainContainer>
      {isSidebar && <SideBar />}
      <Content backgroundColor={backgroundColor}>
        <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
          <React.Suspense fallback={<LoadingPage />}>
            <UpgradePlanBar />
            {props.children}
          </React.Suspense>
        </ResourceNotFoundErrorBoundary>
      </Content>
    </MainContainer>
  );
};

export default MainView;

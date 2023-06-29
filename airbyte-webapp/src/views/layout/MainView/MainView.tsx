import React, { useState, useEffect, useMemo } from "react";
import styled from "styled-components";
import { theme } from "theme";

import { LoadingPage } from "components";
import { CreateStepTypes } from "components/ConnectionStep";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import { useHealth } from "hooks/services/Health";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import {
  UpgradePlanBanner,
  SyncNotificationBanner,
  BillingWarningBanner,
  FailedPaymentBanner,
} from "views/layout/Banners";
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
  position: relative;
`;

const hasCurrentStep = (state: unknown): state is { currentStep: string } => {
  return (
    typeof state === "object" && state !== null && typeof (state as { currentStep?: string }).currentStep === "string"
  );
};

const MainView: React.FC = (props) => {
  const { user } = useUser();
  const { healthData } = useHealth();
  const { usage } = healthData;
  const { isPaymentFailed } = healthData;
  const { pathname, location, push } = useRouter();
  const [usagePercentage, setUsagePercentage] = useState<number>(0);
  const [isSidebar, setIsSidebar] = useState<boolean>(true);
  const [backgroundColor, setBackgroundColor] = useState<string>(theme.backgroundColor);

  useEffect(() => {
    if (usage) {
      setUsagePercentage(usage * 100);
    }
  }, [usage]);

  const hasSidebarRoutes: string[] = useMemo(
    () => [
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
      RoutePaths.Password,
      RoutePaths.Account,
      RoutePaths.Support,
    ],
    []
  );

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
    } else if (lastPathName === RoutePaths.FailedPayment) {
      setBackgroundColor(theme.backgroundColor);
    } else if (isSidebarBol) {
      // In the page with sidebar, the background color of these three pages is #F8F8FE, and the others are the theme background color.
      if (
        lastPathName === RoutePaths.SelectSource ||
        lastPathName === RoutePaths.SelectDestination ||
        lastPathName === RoutePaths.SelectConnection
      ) {
        setBackgroundColor("#F8F8FE");
      } else {
        setBackgroundColor(theme.backgroundColor);
      }
    } else {
      // Other page background color is white.
      setBackgroundColor(theme.white);
    }
    setIsSidebar(isSidebarBol);
  }, [pathname, hasSidebarRoutes, location.state]);

  const onBillingPage = () => {
    push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
  };

  const onFailedPaymentPage = () => {
    push(`/${RoutePaths.FailedPayment}`);
  };

  const isUpgradePlanBanner = (): boolean => {
    let showUpgradePlanBanner = false;
    if (getPaymentStatus(user.status) === PAYMENT_STATUS.Free_Trial) {
      if (!pathname.split("/").includes(RoutePaths.Payment)) {
        showUpgradePlanBanner = true;
      }
    }
    return showUpgradePlanBanner;
  };

  return (
    <MainContainer>
      {isSidebar && <SideBar />}
      <Content backgroundColor={backgroundColor}>
        <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
          <React.Suspense fallback={<LoadingPage />}>
            {isUpgradePlanBanner() && <UpgradePlanBanner onBillingPage={onBillingPage} />}
            {isPaymentFailed && <FailedPaymentBanner onFailedPaymentPage={onFailedPaymentPage} />}
            {usage !== undefined && usagePercentage > 0 && usagePercentage < 100 && (
              <SyncNotificationBanner usagePercentage={usagePercentage} onBillingPage={onBillingPage} />
            )}
            {usage !== undefined && usagePercentage >= 100 && <BillingWarningBanner onBillingPage={onBillingPage} />}
            {props.children}
          </React.Suspense>
        </ResourceNotFoundErrorBoundary>
      </Content>
    </MainContainer>
  );
};

export default MainView;

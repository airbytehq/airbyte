import React, { useState } from "react";
import styled from "styled-components";

import { LoadingPage } from "components";

import { useUser } from "core/AuthContext";
import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import { getStatusAgainstStatusNumber, STATUSES } from "core/Constants/statuses";
import useRouter from "hooks/useRouter";
import { UnauthorizedModal } from "pages/ConnectionPage/pages/AllConnectionsPage/components/UnauthorizedModal";
import { UpgradePlanBar } from "pages/ConnectionPage/pages/AllConnectionsPage/components/UpgradePlanBar";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";
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

const Content = styled.div`
  overflow-y: auto;
  width: 100%;
  height: 100%;
`;

const MainView: React.FC = (props) => {
  const { user } = useUser();
  const { pathname, push } = useRouter();

  const [isAuthorized, setIsAuthorized] = useState<boolean>(false);

  // TODO: not the propersolution but works for now
  const isSidebar =
    !pathname.split("/").includes(RoutePaths.Payment) && !pathname.split("/").includes(RoutePaths.PaymentError);

  const isUpgradePlanBar = (): boolean => {
    let showUpgradePlanBar = false;
    if (getStatusAgainstStatusNumber(user.status) === STATUSES.Free_Trial) {
      if (!pathname.split("/").includes(RoutePaths.Payment)) {
        showUpgradePlanBar = true;
      }
    }
    return showUpgradePlanBar;
  };

  const onUpgradePlan = () => {
    if (
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator_Owner ||
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator
    ) {
      push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
    } else {
      setIsAuthorized(true);
    }
  };

  return (
    <MainContainer>
      {isSidebar && <SideBar />}
      <Content>
        <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
          <React.Suspense fallback={<LoadingPage />}>
            {isAuthorized && <UnauthorizedModal onClose={() => setIsAuthorized(false)} />}
            {isUpgradePlanBar() && <UpgradePlanBar onUpgradePlan={onUpgradePlan} />}
            {props.children}
          </React.Suspense>
        </ResourceNotFoundErrorBoundary>
      </Content>
    </MainContainer>
  );
};

export default MainView;

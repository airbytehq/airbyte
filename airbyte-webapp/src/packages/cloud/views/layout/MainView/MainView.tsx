import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Link, Outlet } from "react-router-dom";
import styled from "styled-components";

import { LoadingPage } from "components";
import { AlertBanner } from "components/base/Banner/AlertBanner";

import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import SideBar from "packages/cloud/views/layout/SideBar";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { InsufficientPermissionsErrorBoundary } from "./InsufficientPermissionsErrorBoundary";

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

const DataBlock = styled.div<{ hasBanner?: boolean }>`
  width: 100%;
  height: 100%;
  padding-top: ${({ hasBanner }) => (hasBanner ? 30 : 0)}px;
`;

const MainView: React.FC = (props) => {
  const { formatMessage } = useIntl();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const showCreditsBanner =
    cloudWorkspace.creditStatus &&
    [
      CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD,
      CreditStatus.NEGATIVE_MAX_THRESHOLD,
      CreditStatus.NEGATIVE_WITHIN_GRACE_PERIOD,
    ].includes(cloudWorkspace.creditStatus) &&
    !cloudWorkspace.trialExpiryTimestamp;

  const alertToShow = showCreditsBanner ? "credits" : cloudWorkspace.trialExpiryTimestamp ? "trial" : undefined;

  const alertMessage = useMemo(() => {
    if (alertToShow === "credits") {
      return (
        <FormattedMessage
          id={`credits.creditsProblem.${cloudWorkspace.creditStatus}`}
          values={{
            lnk: (content: React.ReactNode) => <Link to={CloudRoutes.Credits}>{content}</Link>,
          }}
        />
      );
    } else if (alertToShow === "trial") {
      const { trialExpiryTimestamp } = cloudWorkspace;

      //calculate difference between timestamp (in epoch milliseconds) and now (in epoch milliseconds)
      //empty timestamp is 0
      const trialRemainingMilliseconds = trialExpiryTimestamp ? trialExpiryTimestamp - Date.now() : 0;

      //calculate days (rounding up if decimal)
      const trialRemainingDays = Math.ceil(trialRemainingMilliseconds / (1000 * 60 * 60 * 24));

      return formatMessage({ id: "trial.alertMessage" }, { value: trialRemainingDays });
    }
    return null;
  }, [alertToShow, cloudWorkspace, formatMessage]);

  return (
    <MainContainer>
      <InsufficientPermissionsErrorBoundary errorComponent={<StartOverErrorView />}>
        <SideBar />
        <Content>
          {alertToShow && <AlertBanner message={alertMessage} />}
          <DataBlock hasBanner={!!alertToShow}>
            <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
              <React.Suspense fallback={<LoadingPage />}>{props.children ?? <Outlet />}</React.Suspense>
            </ResourceNotFoundErrorBoundary>
          </DataBlock>
        </Content>
      </InsufficientPermissionsErrorBoundary>
    </MainContainer>
  );
};

export default MainView;

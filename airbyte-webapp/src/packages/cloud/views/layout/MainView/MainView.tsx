import React from "react";
import { Outlet } from "react-router-dom";
import styled from "styled-components";

import { LoadingPage } from "components";

import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import SideBar from "packages/cloud/views/layout/SideBar";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { CreditsProblemBanner } from "./components/CreditsProblemBanner";
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
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const showBanner =
    cloudWorkspace.creditStatus &&
    [
      CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD,
      CreditStatus.NEGATIVE_MAX_THRESHOLD,
      CreditStatus.NEGATIVE_WITHIN_GRACE_PERIOD,
    ].includes(cloudWorkspace.creditStatus);

  return (
    <MainContainer>
      <InsufficientPermissionsErrorBoundary errorComponent={<StartOverErrorView />}>
        <SideBar />
        <Content>
          {cloudWorkspace.creditStatus && showBanner && <CreditsProblemBanner status={cloudWorkspace.creditStatus} />}
          <DataBlock hasBanner={showBanner}>
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

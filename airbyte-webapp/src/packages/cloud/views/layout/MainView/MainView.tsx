import classNames from "classnames";
import React from "react";
import { Outlet } from "react-router-dom";

import { LoadingPage } from "components";

import { useExperimentSpeedyConnection } from "packages/cloud/components/experiments/SpeedyConnection/hooks/useExperimentSpeedyConnection";
import { SpeedyConnectionBanner } from "packages/cloud/components/experiments/SpeedyConnection/SpeedyConnectionBanner";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import SideBar from "packages/cloud/views/layout/SideBar";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { InsufficientPermissionsErrorBoundary } from "./InsufficientPermissionsErrorBoundary";
import styles from "./MainView.module.scss";
import { WorkspaceCreditsBanner } from "./WorkspaceCreditsBanner";

const MainView: React.FC<React.PropsWithChildren<unknown>> = (props) => {
  useIntercom();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const [hasWorkspaceCreditsBanner, setHasCreditsBanner] = React.useState(false);

  // exp-speedy-connection
  const { isExperimentVariant } = useExperimentSpeedyConnection();

  const { hasCorporateEmail } = useAuthService();
  const isTrial = Boolean(cloudWorkspace.trialExpiryTimestamp);
  const showExperimentBanner = isExperimentVariant && isTrial && hasCorporateEmail();

  return (
    <div className={styles.mainContainer}>
      <InsufficientPermissionsErrorBoundary errorComponent={<StartOverErrorView />}>
        <SideBar />
        <div
          className={classNames(styles.content, {
            [styles.alertBanner]: !!hasWorkspaceCreditsBanner && !showExperimentBanner,
            [styles.speedyConnectionBanner]: showExperimentBanner,
          })}
        >
          {showExperimentBanner && <SpeedyConnectionBanner />}
          {/* todo: passing this setter feels like a weird pattern, re-evaluate... is this causing an odd render loop? */}
          <WorkspaceCreditsBanner setHasWorkspaceCreditsBanner={setHasCreditsBanner} />
          <div className={styles.dataBlock}>
            <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
              <React.Suspense fallback={<LoadingPage />}>{props.children ?? <Outlet />}</React.Suspense>
            </ResourceNotFoundErrorBoundary>
          </div>
        </div>
      </InsufficientPermissionsErrorBoundary>
    </div>
  );
};

export default MainView;

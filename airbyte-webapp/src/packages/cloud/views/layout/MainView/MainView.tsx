import classNames from "classnames";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Link, Outlet } from "react-router-dom";

import { LoadingPage } from "components";
import { AlertBanner } from "components/ui/Banner/AlertBanner";

import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { useExperimentSpeedyConnection } from "packages/cloud/components/experiments/SpeedyConnection/hooks/useExperimentSpeedyConnection";
import { SpeedyConnectionBanner } from "packages/cloud/components/experiments/SpeedyConnection/SpeedyConnectionBanner";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import SideBar from "packages/cloud/views/layout/SideBar";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { InsufficientPermissionsErrorBoundary } from "./InsufficientPermissionsErrorBoundary";
import styles from "./MainView.module.scss";

const MainView: React.FC<React.PropsWithChildren<unknown>> = (props) => {
  const { formatMessage } = useIntl();
  useIntercom();
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
  // exp-speedy-connection
  const { isExperimentVariant } = useExperimentSpeedyConnection();
  const { hasCorporateEmail } = useAuthService();
  const isTrial = Boolean(cloudWorkspace.trialExpiryTimestamp);
  const showExperimentBanner = isExperimentVariant && isTrial && hasCorporateEmail();

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

      // calculate difference between timestamp (in epoch milliseconds) and now (in epoch milliseconds)
      // empty timestamp is 0
      const trialRemainingMilliseconds = trialExpiryTimestamp ? trialExpiryTimestamp - Date.now() : 0;

      // calculate days (rounding up if decimal)
      const trialRemainingDays = Math.ceil(trialRemainingMilliseconds / (1000 * 60 * 60 * 24));

      return formatMessage({ id: "trial.alertMessage" }, { value: trialRemainingDays });
    }
    return null;
  }, [alertToShow, cloudWorkspace, formatMessage]);

  return (
    <div className={styles.mainContainer}>
      <InsufficientPermissionsErrorBoundary errorComponent={<StartOverErrorView />}>
        <SideBar />
        <div
          className={classNames(styles.content, {
            [styles.alertBanner]: !!alertToShow && !showExperimentBanner,
            [styles.speedyConnectionBanner]: showExperimentBanner,
          })}
        >
          {showExperimentBanner ? <SpeedyConnectionBanner /> : alertToShow && <AlertBanner message={alertMessage} />}
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

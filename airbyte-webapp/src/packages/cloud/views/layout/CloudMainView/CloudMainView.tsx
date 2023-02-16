import classNames from "classnames";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Outlet } from "react-router-dom";

import { LoadingPage } from "components";
import { CreditsIcon } from "components/icons/CreditsIcon";
import { AlertBanner } from "components/ui/Banner/AlertBanner";
import { Link } from "components/ui/Link";

import { FeatureItem, useFeature } from "hooks/services/Feature";
import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { useExperimentSpeedyConnection } from "packages/cloud/components/experiments/SpeedyConnection/hooks/useExperimentSpeedyConnection";
import { SpeedyConnectionBanner } from "packages/cloud/components/experiments/SpeedyConnection/SpeedyConnectionBanner";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { RoutePaths } from "pages/routePaths";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import { AirbyteHomeLink } from "views/layout/SideBar/AirbyteHomeLink";
import { MenuContent } from "views/layout/SideBar/components/MenuContent";
import { NavItem } from "views/layout/SideBar/components/NavItem";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import { MainNavItems } from "views/layout/SideBar/MainNavItems";
import { SideBar } from "views/layout/SideBar/SideBar";

import styles from "./CloudMainView.module.scss";
import { CloudResourcesDropdown } from "./CloudResourcesDropdown";
import { CloudSupportDropdown } from "./CloudSupportDropdown";
import { InsufficientPermissionsErrorBoundary } from "./InsufficientPermissionsErrorBoundary";
import { LOW_BALANCE_CREDIT_THRESHOLD } from "../../credits/CreditsPage/components/LowCreditBalanceHint/LowCreditBalanceHint";
import { WorkspacePopout } from "../../workspaces/WorkspacePopout";

const CloudMainView: React.FC<React.PropsWithChildren<unknown>> = (props) => {
  useIntercom();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const isAllowUpdateConnectorsEnabled = useFeature(FeatureItem.AllowUpdateConnectors);

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

      return (
        <FormattedMessage
          id="trial.alertMessage"
          values={{
            remainingDays: trialRemainingDays,
            lnk: (cta: React.ReactNode) => <Link to={CloudRoutes.Credits}>{cta}</Link>,
          }}
        />
      );
    }
    return null;
  }, [alertToShow, cloudWorkspace]);

  return (
    <div className={styles.mainContainer}>
      <InsufficientPermissionsErrorBoundary errorComponent={<StartOverErrorView />}>
        <SideBar>
          <AirbyteHomeLink />
          <WorkspacePopout>
            {({ onOpen, value }) => (
              <button className={styles.workspaceButton} onClick={onOpen} data-testid="workspaceButton">
                {value}
              </button>
            )}
          </WorkspacePopout>
          <MenuContent>
            <MainNavItems />
            <MenuContent>
              <NavItem
                to={CloudRoutes.Credits}
                icon={<CreditsIcon />}
                label={<FormattedMessage id="sidebar.credits" />}
                testId="creditsButton"
                withNotification={cloudWorkspace.remainingCredits <= LOW_BALANCE_CREDIT_THRESHOLD}
              />
              <CloudResourcesDropdown /> <CloudSupportDropdown />
              <NavItem
                label={<FormattedMessage id="sidebar.settings" />}
                icon={<SettingsIcon />}
                to={RoutePaths.Settings}
                withNotification={isAllowUpdateConnectorsEnabled}
              />
            </MenuContent>
          </MenuContent>
        </SideBar>
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

export default CloudMainView;

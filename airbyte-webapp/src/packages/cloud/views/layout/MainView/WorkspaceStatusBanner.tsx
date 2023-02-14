import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import { AlertBanner } from "components/ui/Banner/AlertBanner";

import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

interface WorkspaceStatusBannerProps {
  setHasWorkspaceCreditsBanner: (hasWorkspaceCreditsBanner: boolean) => void;
}
export const WorkspaceStatusBanner: React.FC<WorkspaceStatusBannerProps> = ({ setHasWorkspaceCreditsBanner }) => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const negativeCreditsStatus = useMemo(() => {
    return (
      cloudWorkspace.creditStatus &&
      [
        CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD,
        CreditStatus.NEGATIVE_MAX_THRESHOLD,
        CreditStatus.NEGATIVE_WITHIN_GRACE_PERIOD,
      ].includes(cloudWorkspace.creditStatus)
    );
  }, [cloudWorkspace.creditStatus]);

  /**
   * Priority for showing banners in the UI:
   * 1. Are credits 0 or negative?  Show the credits banner
   * 2. Are they in a trial?  Show the trial countdown banner
   * 3. Are they pre-trial? Show the pre-trial banner
   * 4. Otherwise, no banner about credits
   */
  const workspaceCreditsBannerContent = useMemo(() => {
    // TODO: are all of these statuses/messages valid now that we've changed our grace period policy?
    if (negativeCreditsStatus) {
      return (
        <FormattedMessage
          id="credits.creditsProblem"
          values={{
            lnk: (content: React.ReactNode) => <Link to={CloudRoutes.Credits}>{content}</Link>,
          }}
        />
      );
    }
    // TODO: wait for this endpoint to be merged and add it to the types :)
    if (cloudWorkspace.workspaceTrialStatus === "pre_trial") {
      return <FormattedMessage id="trial.preTrialAlertMessage" />;
    }

    // TODO: wait for this endpoint to be merged and add it to the types :)
    if (cloudWorkspace.workspaceTrialStatus === "in_trial") {
      const { trialExpiryTimestamp } = cloudWorkspace;

      // calculate difference between timestamp (in epoch milliseconds) and now (in epoch milliseconds)
      const trialRemainingMilliseconds = trialExpiryTimestamp ? trialExpiryTimestamp - Date.now() : 0;
      if (trialRemainingMilliseconds < 0) {
        return null;
      }
      // calculate days (rounding up if decimal)
      const trialRemainingDays = Math.ceil(trialRemainingMilliseconds / (1000 * 60 * 60 * 24));

      return <FormattedMessage id="trial.alertMessage" values={{ value: trialRemainingDays }} />;
    }

    // otherwise, show nothing
    return null;
  }, [cloudWorkspace, negativeCreditsStatus]);

  setHasWorkspaceCreditsBanner(!!workspaceCreditsBannerContent);

  return <>{!!workspaceCreditsBannerContent && <AlertBanner message={workspaceCreditsBannerContent} />}</>;
};

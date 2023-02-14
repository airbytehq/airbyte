import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import { AlertBanner } from "components/ui/Banner/AlertBanner";

import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { CreditStatus, WorkspaceTrialStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
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
  const workspaceCreditsBannerContent = useMemo(() => {
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

    if (cloudWorkspace.workspaceTrialStatus === WorkspaceTrialStatus.PRE_TRIAL) {
      return <FormattedMessage id="trial.preTrialAlertMessage" />;
    }

    if (cloudWorkspace.workspaceTrialStatus === WorkspaceTrialStatus.IN_TRIAL) {
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

    return null;
  }, [cloudWorkspace, negativeCreditsStatus]);

  setHasWorkspaceCreditsBanner(!!workspaceCreditsBannerContent);

  return <>{!!workspaceCreditsBannerContent && <AlertBanner message={workspaceCreditsBannerContent} />}</>;
};

import { useExperiment } from "hooks/services/Experiment";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

export const useExperimentSpeedyConnection = () => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const isVariantEnabled = useExperiment("onbarding.speedyConnection", false);

  const isTrial = Boolean(cloudWorkspace.trialExpiryTimestamp);
  const timestamp = localStorage.getItem("exp-speedy-connection-timestamp");
  const expiredOfferDate = timestamp ? String(timestamp) : String(0);

  const now = new Date();
  const isExperimentVariant = isTrial && expiredOfferDate && new Date(expiredOfferDate) >= now && isVariantEnabled;
  return { isExperimentVariant, expiredOfferDate };
};

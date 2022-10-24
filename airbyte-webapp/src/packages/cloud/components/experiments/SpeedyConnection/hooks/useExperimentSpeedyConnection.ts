import { useExperiment } from "hooks/services/Experiment";
import { useCurrentWorkspaceState } from "services/workspaces/WorkspacesService";

export const useExperimentSpeedyConnection = () => {
  const { hasConnections } = useCurrentWorkspaceState();
  const isVariantEnabled = useExperiment("onboarding.speedyConnection", false);

  const timestamp = localStorage.getItem("exp-speedy-connection-timestamp");
  const expiredOfferDate = timestamp ? String(timestamp) : String(0);

  const now = new Date();
  const isExperimentVariant =
    !hasConnections && expiredOfferDate && new Date(expiredOfferDate) >= now && isVariantEnabled;
  return { isExperimentVariant, expiredOfferDate };
};

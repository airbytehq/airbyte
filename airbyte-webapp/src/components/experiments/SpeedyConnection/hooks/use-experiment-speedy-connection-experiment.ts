import { useMemo } from "react";

import { usePostHog } from "hooks/services/PostHogExperiment/PostHogExperimentService";

export const useExperimentSpeedyConnection = () => {
  // const workspace = useCurrentWorkspace();
  // const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const isTrial = true;
  // const isTrial = Boolean(cloudWorkspace.trialExpiryTimestamp);
  const expiredOfferDate = JSON.parse(localStorage.getItem("exp-speedy-connection-timestamp") ?? "");
  // const { hasConnections, hasDestinations, hasSources } = useCurrentWorkspaceState();
  const { posthog } = usePostHog();
  const isVariantEnabled = useMemo(() => posthog.getFeatureFlag("exp-speedy-connection") === "test", []);
  const now = new Date();
  const isExperimentVariant = isTrial && expiredOfferDate && new Date(expiredOfferDate) >= now && isVariantEnabled;
  return { isExperimentVariant, expiredOfferDate };
};

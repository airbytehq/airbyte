import { useMemo } from "react";

import { usePostHog } from "hooks/services/PostHogExperiment/PostHogExperimentService";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

export const useExperimentSpeedyConnection = () => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const isTrial = Boolean(cloudWorkspace.trialExpiryTimestamp);
  const expiredOfferDate = JSON.parse(localStorage.getItem("exp-speedy-connection-timestamp") ?? "");

  const { posthog } = usePostHog();
  const isVariantEnabled = useMemo(() => posthog.getFeatureFlag("exp-speedy-connection") === "test", [posthog]);
  const now = new Date();
  const isExperimentVariant = isTrial && expiredOfferDate && new Date(expiredOfferDate) >= now && isVariantEnabled;
  return { isExperimentVariant, expiredOfferDate };
};

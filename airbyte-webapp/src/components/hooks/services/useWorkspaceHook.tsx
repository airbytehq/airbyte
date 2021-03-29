import { useFetcher, useResource } from "rest-hooks";

import config from "config";
import WorkspaceResource, { Workspace } from "core/resources/Workspace";
import { AnalyticsService } from "core/analytics/AnalyticsService";

const useWorkspace = (): {
  workspace: Workspace;
  setInitialSetupConfig: (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => Promise<void>;
  finishOnboarding: (skipStep?: string) => Promise<void>;
} => {
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const finishOnboarding = async (skipStep?: string) => {
    if (skipStep) {
      AnalyticsService.track("Skip Onboarding", {
        step: skipStep,
      });
    }

    await updateWorkspace(
      {},
      {
        workspaceId: workspace.workspaceId,
        initialSetupComplete: workspace.initialSetupComplete,
        anonymousDataCollection: workspace.anonymousDataCollection,
        news: workspace.news,
        securityUpdates: workspace.securityUpdates,
        displaySetupWizard: false,
      }
    );
  };

  const setInitialSetupConfig = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateWorkspace(
      {},
      {
        workspaceId: config.ui.workspaceId,
        initialSetupComplete: true,
        displaySetupWizard: true,
        ...data,
      }
    );
  };

  return {
    workspace,
    finishOnboarding,
    setInitialSetupConfig,
  };
};

export default useWorkspace;

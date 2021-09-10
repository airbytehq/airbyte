import { useFetcher, useResource } from "rest-hooks";

import WorkspaceResource, { Workspace } from "core/resources/Workspace";
import NotificationsResource, {
  Notifications,
} from "core/resources/Notifications";
import { useGetService } from "core/servicesProvider";
import { useAnalytics } from "../useAnalytics";

export const usePickFirstWorkspace = (): Workspace => {
  const { workspaces } = useResource(WorkspaceResource.listShape(), {});

  return workspaces[0];
};

const useCurrentWorkspace = (): Workspace => {
  const workspaceProviderService = useGetService<() => Workspace>(
    "currentWorkspaceProvider"
  );

  return workspaceProviderService();
};

export type WebhookPayload = {
  webhook: string;
  sendOnSuccess: boolean;
  sendOnFailure: boolean;
};

const useWorkspace = (): {
  workspace: Workspace;
  updatePreferences: (data: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => Promise<Workspace>;
  updateWebhook: (data: WebhookPayload) => Promise<Workspace>;
  testWebhook: (data: WebhookPayload) => Promise<Notifications>;
  setInitialSetupConfig: (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => Promise<Workspace>;
  finishOnboarding: (skipStep?: string) => Promise<void>;
} => {
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const tryWebhookUrl = useFetcher(NotificationsResource.tryShape());
  const workspace = useCurrentWorkspace();

  const analyticsService = useAnalytics();

  const finishOnboarding = async (skipStep?: string) => {
    if (skipStep) {
      analyticsService.track("Skip Onboarding", {
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
  }) =>
    await updateWorkspace(
      {},
      {
        workspaceId: workspace.workspaceId,
        initialSetupComplete: true,
        displaySetupWizard: true,
        ...data,
      }
    );

  const updatePreferences = async (data: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) =>
    await updateWorkspace(
      {},
      {
        workspaceId: workspace.workspaceId,
        initialSetupComplete: workspace.initialSetupComplete,
        displaySetupWizard: workspace.displaySetupWizard,
        notifications: workspace.notifications,
        ...data,
      }
    );

  const testWebhook = async (data: WebhookPayload) =>
    await tryWebhookUrl(
      {
        notificationType: "slack",
        sendOnSuccess: data.sendOnSuccess,
        sendOnFailure: data.sendOnFailure,
        slackConfiguration: {
          webhook: data.webhook,
        },
      },
      {}
    );

  const updateWebhook = async (data: WebhookPayload) =>
    await updateWorkspace(
      {},
      {
        workspaceId: workspace.workspaceId,
        initialSetupComplete: workspace.initialSetupComplete,
        displaySetupWizard: workspace.displaySetupWizard,
        anonymousDataCollection: workspace.anonymousDataCollection,
        news: workspace.news,
        securityUpdates: workspace.securityUpdates,
        notifications: [
          {
            notificationType: "slack",
            sendOnSuccess: data.sendOnSuccess,
            sendOnFailure: data.sendOnFailure,
            slackConfiguration: {
              webhook: data.webhook,
            },
          },
        ],
      }
    );

  return {
    workspace,
    finishOnboarding,
    setInitialSetupConfig,
    updatePreferences,
    updateWebhook,
    testWebhook,
  };
};

export { useCurrentWorkspace, useWorkspace };
export default useWorkspace;

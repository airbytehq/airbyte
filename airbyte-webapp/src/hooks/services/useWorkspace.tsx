import { useMutation } from "react-query";

import { Action, Namespace } from "core/analytics";
import { NotificationService } from "core/domain/notification/NotificationService";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useInitService } from "services/useInitService";
import { useCurrentWorkspace, useUpdateWorkspace } from "services/workspaces/WorkspacesService";

import { useConfig } from "../../config";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";

export interface WebhookPayload {
  webhook?: string;
  sendOnSuccess?: boolean;
  sendOnFailure?: boolean;
}

function useGetNotificationService() {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(() => new NotificationService(config.apiUrl, middlewares), [config.apiUrl, middlewares]);
}

const useWorkspace = () => {
  const notificationService = useGetNotificationService();
  const { mutateAsync: updateWorkspace } = useUpdateWorkspace();
  const workspace = useCurrentWorkspace();

  const analyticsService = useAnalyticsService();

  const setInitialSetupConfig = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    const result = await updateWorkspace({
      workspaceId: workspace.workspaceId,
      initialSetupComplete: true,
      displaySetupWizard: true,
      ...data,
    });

    analyticsService.track(Namespace.ONBOARDING, Action.PREFERENCES, {
      actionDescription: "Setup preferences set",
      email: data.email,
      anonymized: data.anonymousDataCollection,
      subscribed_newsletter: data.news,
      subscribed_security: data.securityUpdates,
    });

    return result;
  };

  const updatePreferences = async (data: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) =>
    await updateWorkspace({
      workspaceId: workspace.workspaceId,
      initialSetupComplete: workspace.initialSetupComplete,
      displaySetupWizard: workspace.displaySetupWizard,
      notifications: workspace.notifications,
      ...data,
    });

  const updateWebhook = async (data: WebhookPayload) =>
    await updateWorkspace({
      workspaceId: workspace.workspaceId,
      initialSetupComplete: workspace.initialSetupComplete,
      displaySetupWizard: workspace.displaySetupWizard,
      anonymousDataCollection: !!workspace.anonymousDataCollection,
      news: !!workspace.news,
      securityUpdates: !!workspace.securityUpdates,
      notifications: [
        {
          notificationType: "slack",
          sendOnSuccess: !!data.sendOnSuccess,
          sendOnFailure: !!data.sendOnFailure,
          slackConfiguration: {
            webhook: data.webhook ?? "",
          },
        },
      ],
    });

  const tryWebhookUrl = useMutation((data: WebhookPayload) =>
    notificationService.try({
      notificationType: "slack",
      sendOnSuccess: !!data.sendOnSuccess,
      sendOnFailure: !!data.sendOnFailure,
      slackConfiguration: {
        webhook: data.webhook ?? "",
      },
    })
  );

  return {
    setInitialSetupConfig,
    updatePreferences,
    updateWebhook,
    testWebhook: tryWebhookUrl.mutateAsync,
  };
};

export { useCurrentWorkspace, useWorkspace };
export default useWorkspace;

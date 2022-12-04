export interface Notification {
  notificationType: string;
  sendOnSuccess: boolean;
  sendOnFailure: boolean;
  slackConfiguration: {
    webhook: string;
  };
}

export interface Workspace {
  workspaceId: string;
  customerId: string;
  name: string;
  email: string;
  slug: string;
  initialSetupComplete: boolean;
  anonymousDataCollection: boolean;
  news: boolean;
  securityUpdates: boolean;
  displaySetupWizard: boolean;
  notifications: Notification[];
}

export interface WorkspaceState {
  hasSources: boolean;
  hasDestinations: boolean;
  hasConnections: boolean;
}

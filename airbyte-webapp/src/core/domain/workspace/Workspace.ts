export interface Notification {
  notificationType: string;
  sendOnSuccess: boolean;
  sendOnFailure: boolean;
  slackConfiguration: {
    webhook: string;
  };
}

export interface WorkspaceState {
  hasSources: boolean;
  hasDestinations: boolean;
  hasConnections: boolean;
}

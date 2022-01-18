export interface CloudWorkspace {
  name: string;
  workspaceId: string;
  billingUserId: string;
  remainingCredits: number;
}

export interface CloudWorkspaceUsage {
  workspaceId: string;
  creditConsumptionByConnector: {
    connectionId: string;
    creditsConsumed: number;
  }[];
  creditConsumptionByDay: {
    date: [number, number, number];
    creditsConsumed: number;
  }[];
}

export interface CloudWorkspace {
  name: string;
  workspaceId: string;
  billingUserId: string;
  remainingCredits: number;
}

export interface CreditConsumptionByConnector {
  connectionId: string;
  creditsConsumed: number;
  destinationConnectionName: string;
  destinationDefinitionId: string;
  destinationDefinitionName: string;
  destinationId: string;
  sourceConnectionName: string;
  sourceDefinitionId: string;
  sourceDefinitionName: string;
  sourceId: string;
}

export interface CloudWorkspaceUsage {
  workspaceId: string;
  creditConsumptionByConnector: CreditConsumptionByConnector[];
  creditConsumptionByDay: {
    date: [number, number, number];
    creditsConsumed: number;
  }[];
}

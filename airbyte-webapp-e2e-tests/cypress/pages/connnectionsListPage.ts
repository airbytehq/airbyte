import { Connection } from "commands/api/types";
import { getWorkspaceId } from "commands/api/workspace";

const statusCell = (connectionId: string) => `[data-testId='statusCell-${connectionId}']`;
const changesStatusIcon = (type: string) => `[data-testId='changesStatusIcon-${type}']`;
const manualSyncButton = "button[data-testId='manual-sync-button']";

export const visitConnectionsListPage = () => {
  cy.intercept("**/web_backend/connections/list").as("listConnections");
  cy.visit(`/workspaces/${getWorkspaceId()}/connections`);
  cy.wait("@listConnections", { timeout: 20000 });
};

export const getSchemaChangeIcon = (connection: Connection, type: "breaking" | "non_breaking") =>
  cy.get(`${statusCell(connection.connectionId)} ${changesStatusIcon(type)}`);

export const getManualSyncButton = (connection: Connection) =>
  cy.get(`${statusCell(connection.connectionId)} ${manualSyncButton}`);

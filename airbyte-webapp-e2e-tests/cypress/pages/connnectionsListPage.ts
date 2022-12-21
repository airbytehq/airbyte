import { Connection } from "commands/api/types";
import { getWorkspaceId } from "commands/api/workspace";

export const visitConnectionsListPage = () => {
  cy.intercept("**/web_backend/connections/list").as("listConnections");
  cy.visit(`/workspaces/${getWorkspaceId()}/connections`);
  cy.wait("@listConnections");
};

export const getSchemaChangeIcon = (connection: Connection, type: "breaking" | "non_breaking") =>
  cy.get(`[data-testId='statusCell-${connection.connectionId}'] [data-testId='changesStatusIcon-${type}']`);

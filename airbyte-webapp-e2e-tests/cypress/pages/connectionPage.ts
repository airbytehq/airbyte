import { Connection } from "commands/api/types";
import { getWorkspaceId } from "commands/api/workspace";

export const visitConnectionPage = (connection: Connection, tab = "") => {
  cy.intercept("**/web_backend/connections/get").as("getConnection");
  cy.visit(`/workspaces/${getWorkspaceId()}/connections/${connection.connectionId}/${tab}`);
  cy.wait("@getConnection");
};

import { Connection } from "commands/api/types";
import { getWorkspaceId } from "commands/api/workspace";

const replicationTab = "div[data-id='replication-step']";
const syncEnabledSwitch = "[data-testid='enabledControl-switch']";

export const visit = (connection: Connection, tab = "") => {
  cy.intercept("**/web_backend/connections/get").as("getConnection");
  cy.visit(`/workspaces/${getWorkspaceId()}/connections/${connection.connectionId}/${tab}`);
  cy.wait("@getConnection", { timeout: 20000 });
};

export const goToReplicationTab = () => {
  cy.get(replicationTab).click();
};

export const getSyncEnabledSwitch = () => cy.get(syncEnabledSwitch);

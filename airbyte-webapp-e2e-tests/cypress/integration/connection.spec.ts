import { deleteEntity } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";

describe("Connection main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new connection", () => {
    createTestConnection("Test connection source cypress", "Test destination cypress");

    cy.get("div").contains("Test connection source cypress").should("exist");
    cy.get("div").contains("Test destination cypress").should("exist");
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/updateNew").as("updateConnection");

    createTestConnection("Test update connection source cypress", "Test update connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test update connection source cypress").click();
    cy.get("div").contains("Test update connection destination cypress").click();

    cy.get("div[data-id='replication-step']").click();

    cy.get("div[data-testid='schedule']").click();
    cy.get("div[data-testid='Every 5 minutes']").click();
    cy.get("button[type=submit]").first().click();
    cy.wait("@updateConnection");
    cy.get("span[data-id='success-result']").should("exist");
});

  it("Delete connection", () => {
    createTestConnection("Test delete connection source cypress", "Test delete connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test delete connection source cypress").click();
    cy.get("div").contains("Test delete connection destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    deleteEntity();

    deleteSource("Test delete connection source cypress");
    deleteDestination("Test delete connection destination cypress");
  });
});
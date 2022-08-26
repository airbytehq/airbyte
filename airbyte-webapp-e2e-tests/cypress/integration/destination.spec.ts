import { createTestDestination, deleteDestination, updateDestination } from "commands/destination";
import { initialSetupCompleted } from "commands/workspaces";

describe("Destination main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new destination", () => {
    createTestDestination("Test destination cypress");

    cy.url().should("include", `/destination/`);
  });

  it("Update destination", () => {
    createTestDestination("Test destination cypress for update");
    updateDestination("Test destination cypress for update", "connectionConfiguration.destination_path", "/local/my-json");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete destination", () => {
    createTestDestination("Test destination cypress for delete");
    deleteDestination("Test destination cypress for delete");

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress for delete").should("not.exist");
  });
});
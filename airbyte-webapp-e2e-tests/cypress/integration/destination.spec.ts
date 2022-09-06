import { createLocalJsonDestination, deleteDestination, updateDestination } from "commands/destination";
import { initialSetupCompleted } from "commands/workspaces";

describe("Destination main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new destination", () => {
    createLocalJsonDestination("Test destination cypress", "/local");

    cy.url().should("include", `/destination/`);
  });

  it("Update destination", () => {
    createLocalJsonDestination("Test destination cypress for update", "/local");
    updateDestination("Test destination cypress for update", "connectionConfiguration.destination_path", "/local/my-json");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete destination", () => {
    createLocalJsonDestination("Test destination cypress for delete", "/local");
    deleteDestination("Test destination cypress for delete");

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress for delete").should("not.exist");
  });
});
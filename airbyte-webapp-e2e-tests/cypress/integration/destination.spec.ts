import { appendRandomString } from "commands/common";
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
    const destName = appendRandomString("Test destination cypress for update");
    createLocalJsonDestination(destName, "/local");
    updateDestination(destName, "connectionConfiguration.destination_path", "/local/my-json");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete destination", () => {
    const destName = appendRandomString("Test destination cypress for delete");
    createLocalJsonDestination(destName, "/local");
    deleteDestination(destName);

    cy.visit("/destination");
    cy.get("div").contains(destName).should("not.exist");
  });
});

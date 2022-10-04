import { appendRandomString } from "commands/common";
import { createPostgresSource, deleteSource, updateSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";

describe("Source main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new source", () => {
    createPostgresSource("Test source cypress");

    cy.url().should("include", `/source/`);
  });

  //TODO: add update source on some other connector or create 1 more user for pg
  it.skip("Update source", () => {
    const sourceName = appendRandomString("Test source cypress for update");
    createPostgresSource(sourceName);
    updateSource(sourceName, "connectionConfiguration.start_date", "2020-11-11");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='2020-11-11']").should("exist");
  });

  it("Delete source", () => {
    const sourceName = appendRandomString("Test source cypress for delete");
    createPostgresSource(sourceName);
    deleteSource(sourceName);

    cy.visit("/");
    cy.get("div").contains(sourceName).should("not.exist");
  });
});

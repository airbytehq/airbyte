import { createPostgresSource, deleteSource, updateSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";

describe("Source main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new source", () => {
    createPostgresSource("Test source cypress", "localhost", "{selectAll}{del}5433", "airbyte_ci", "postgres", "secret_password");

    cy.url().should("include", `/source/`);
  });

  //TODO: add update source on some other connector or create 1 more user for pg
  it.skip("Update source", () => {
    createPostgresSource("Test source cypress for update", "localhost", "{selectAll}{del}5433", "airbyte_ci", "postgres", "secret_password");
    updateSource("Test source cypress for update", "connectionConfiguration.start_date", "2020-11-11");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='2020-11-11']").should("exist");
  });

  it("Delete source", () => {
    createPostgresSource("Test source cypress for delete", "localhost", "{selectAll}{del}5433", "airbyte_ci", "postgres", "secret_password");
    deleteSource("Test source cypress for delete");

    cy.visit("/");
    cy.get("div").contains("Test source cypress for delete").should("not.exist");
  });
});
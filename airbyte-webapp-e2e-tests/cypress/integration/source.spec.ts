import { appendRandomString, submitButtonClick } from "commands/common";
import { createPostgresSource, deleteSource, updateSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import { goToSourcePage, openNewSourceForm } from "pages/sourcePage";
import { openHomepage } from "pages/sidebar";
import { selectServiceType } from "pages/createConnectorPage";
import { fillPokeAPIForm } from "commands/connector";

describe("Source main actions", () => {
  beforeEach(() => initialSetupCompleted());

  it("Create new source", () => {
    cy.intercept("/api/v1/sources/create").as("createSource");
    createPostgresSource("Test source cypress");

    cy.wait("@createSource", { timeout: 30000 }).then((interception) => {
      assert("include", `/source/${interception.response?.body.Id}`);
    });
  });

  // TODO: add update source on some other connector or create 1 more user for pg
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

describe("Unsaved changes modal", () => {
  beforeEach(() => initialSetupCompleted());

  it("Check leaving Source page without any changes", () => {
    goToSourcePage();
    openNewSourceForm();

    openHomepage();

    cy.url().should("include", "/connections");
    cy.get("[data-testid='confirmationModal']").should("not.exist");
  });

  it("Check leaving Source page without any changes after selection type", () => {
    goToSourcePage();
    openNewSourceForm();
    selectServiceType("PokeAPI");

    openHomepage();

    cy.url().should("include", "/connections");
    cy.get("[data-testid='confirmationModal']").should("not.exist");
  });

  it("Check leaving Source page without any changes", () => {
    goToSourcePage();
    openNewSourceForm();
    fillPokeAPIForm("testName", "ditto");

    openHomepage();

    cy.get("[data-testid='confirmationModal']").should("exist");
    cy.get("[data-testid='confirmationModal']").contains("Discard changes");
    cy.get("[data-testid='confirmationModal']").contains(
      "There are unsaved changes. Are you sure you want to discard your changes?"
    );
  });

  it("Check leaving Source page after failing testing", () => {
    cy.intercept("/api/v1/scheduler/sources/check_connection").as("checkSourceUpdateConnection");

    goToSourcePage();
    openNewSourceForm();
    fillPokeAPIForm("testName", "name");
    submitButtonClick();

    cy.wait("@checkSourceUpdateConnection", { timeout: 5000 });

    openHomepage();

    cy.get("[data-testid='confirmationModal']").should("exist");
    cy.get("[data-testid='confirmationModal']").contains("Discard changes");
    cy.get("[data-testid='confirmationModal']").contains(
      "There are unsaved changes. Are you sure you want to discard your changes?"
    );
  });
});

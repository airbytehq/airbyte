describe("Root route", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Create new source", () => {
    cy.intercept("/api/v1/web_backend/connections/list").as("getConnectionsList");
    cy.intercept("/api/v1/source_definition_specifications/get").as("getSpecifications");
    cy.intercept("/api/v1/scheduler/sources/check_connection").as("checkConnection");
    cy.intercept("/api/v1/sources/create").as("createSource");

    cy.wait("@getConnectionsList");

    cy.get("button[data-id='new-source'").click();
    cy.url().should("eq", `${Cypress.config().baseUrl}/source/new-source`);

    cy.get("input[name=name]").type("Test source cypress");
    cy.get("div[role=combobox]").click();
    cy.get("div").contains("Exchange Rates Api").click();

    cy.wait("@getSpecifications");

    cy.get("input[name='connectionConfiguration.base']").type("USD");
    cy.get("input[name='connectionConfiguration.start_date']").type("2020-12-12");

    cy.get("button[type=submit]").click();
    cy.wait("@checkConnection");
    cy.wait("@createSource");
    cy.url().should("include", `${Cypress.config().baseUrl}/source/`);
  });

  it("Update source", () => {
    cy.intercept("/api/v1/sources/check_connection_for_update").as("checkConnection");
    cy.intercept("/api/v1/sources/update").as("updateSource");

    cy.get("div").contains("Test source cypress").click();
    cy.url().should("include", `${Cypress.config().baseUrl}/source/`);

    cy.get("div[data-id='settings-step']").click();

    cy.get("input[name='connectionConfiguration.start_date']").clear().type("2020-11-11");
    cy.get("button[type=submit]").click();

    cy.wait("@checkConnection");
    cy.wait("@updateSource");
    cy.wait(1000);

    cy.get("span[data-id='success-result']").should("exist");
    cy.get("input[value='2020-11-11']").should("exist");
  });

  it("Delete 'Test source cypress' source", () => {
    cy.get("div").contains("Test source cypress").click();
    cy.url().should("include", `${Cypress.config().baseUrl}/source/`);

    cy.get("div[data-id='settings-step']").click();
    cy.get("button[data-id='open-delete-modal']").click();
    cy.get("button[data-id='delete']").click();

    cy.visit("/");
    cy.get("div").contains("Test source cypress").should("not.exist");
  });
});
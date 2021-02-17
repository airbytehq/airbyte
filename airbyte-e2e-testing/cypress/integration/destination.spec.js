describe("Root route", () => {
  beforeEach(() => {
    cy.visit("/destination");
  });

  it("Create new destination", () => {
    cy.intercept("/api/v1/web_backend/connections/list").as("getConnectionsList");
    cy.intercept("/api/v1/destination_definition_specifications/get").as("getSpecifications");
    cy.intercept("/api/v1/scheduler/destinations/check_connection").as("checkConnection");
    cy.intercept("/api/v1/destinations/create").as("createDestination");

    cy.wait("@getConnectionsList");

    cy.get("button").contains("+ new destination").click();
    cy.url().should("eq", `${Cypress.config().baseUrl}/destination/new-destination`);

    cy.get("input[name=name]").type("Test destination cypress");
    cy.get("div[role=combobox]").click();
    cy.get("div").contains("Local JSON").click();

    cy.wait("@getSpecifications");

    cy.get("input[name='connectionConfiguration.destination_path']").type("/local");

    cy.get("button[type=submit]").click();
    cy.wait("@checkConnection");
    cy.wait("@createDestination");
    cy.url().should("include", `${Cypress.config().baseUrl}/destination/`);
  });

  it("Update destination", () => {
    cy.intercept("/api/v1/destinations/check_connection_for_update").as("checkConnection");
    cy.intercept("/api/v1/destinations/update").as("updateDestination");

    cy.get("div").contains("Test destination cypress").click();
    cy.url().should("include", `${Cypress.config().baseUrl}/destination/`);

    cy.get("div").contains("Settings").click();

    cy.get("input[name='connectionConfiguration.destination_path']").type("/my-json");
    cy.get("button[type=submit]").click();

    cy.wait("@checkConnection");
    cy.wait("@updateDestination");
    cy.wait(1000);

    cy.get("span").contains("Your changes were saved!").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete 'Test destination cypress' destination", () => {
    cy.get("div").contains("Test destination cypress").click();
    cy.url().should("include", `${Cypress.config().baseUrl}/destination/`);

    cy.get("div").contains("Settings").click();
    cy.get("button").contains("Delete this destination").click();
    cy.get("button[type=button]").contains("Delete").click();

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress").should("not.exist");
  });
});
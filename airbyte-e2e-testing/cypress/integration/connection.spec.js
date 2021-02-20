describe("Connection main actions", () => {
  before(() => {
    require('./utils.js');
  });

  beforeEach(() => {
    cy.visit("/");
  });

  it("Create new connection", () => {
    cy.intercept("/api/v1/sources/check_connection").as("checkConnectionSource");
    cy.intercept("/api/v1/destinations/check_connection").as("checkConnectionDestination");

    cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
    cy.intercept("/api/v1/connections/create").as("createConnection");

    cy.createTestSource("Test source cypress");
    cy.createTestDestination("Test destination cypress");
    cy.wait(3000);

    cy.get("div[role=combobox]").click();
    cy.get("div").contains("Test source cypress").click();
    cy.wait("@checkConnectionSource");
    cy.wait("@checkConnectionDestination");


    cy.wait("@discoverSchema");

    cy.get("div[role=combobox]").last().click();
    cy.get("div[data-id='manual']").click();
    cy.submit();

    cy.wait("@createConnection");

    cy.get("div").contains("Test source cypress").should("exist");
    cy.get("div").contains("Test destination cypress").should("exist");
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    cy.get("div").contains("Test source cypress").click();
    cy.get("div").contains("Test destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    cy.get("div[role=combobox]").last().click();
    cy.get("div[data-id='5m']").click();
    cy.submit();
    cy.wait("@updateConnection");
    cy.get("span[data-id='success-result']").should("exist");

    cy.get("div[data-id='status-step']").click();
    cy.get("div").contains("5 min").should("exist");
});

  it("Delete connection", () => {
    cy.get("div").contains("Test source cypress").click();
    cy.get("div").contains("Test destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    cy.deleteEntity();

    cy.deleteSource("Test source cypress");
    cy.deleteDestination("Test destination cypress");
  });
});
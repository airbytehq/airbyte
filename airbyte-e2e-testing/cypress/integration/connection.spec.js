describe("Root route", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Create new connection", () => {
    cy.intercept("/api/v1/web_backend/connections/list").as("getConnectionsList");
    cy.intercept("/api/v1/source_definition_specifications/get").as("getSpecifications");
    cy.intercept("/api/v1/destination_definition_specifications/get").as("getSpecificationsDestination");
    cy.intercept("/api/v1/scheduler/sources/check_connection").as("checkConnection");
    cy.intercept("/api/v1/sources/check_connection").as("checkConnectionSource");
    cy.intercept("/api/v1/sources/create").as("createSource");
    cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
    cy.intercept("/api/v1/connections/create").as("createConnection");

    cy.intercept("/api/v1/scheduler/destinations/check_connection").as("checkConnectionDestination");
    cy.intercept("/api/v1/destinations/create").as("createDestination");

    cy.wait("@getConnectionsList");

    cy.get("button[data-id='new-source'").click();

    cy.get("input[name=name]").type("Test source cypress");
    cy.get("div[role=combobox]").click();
    cy.get("div").contains("Exchange Rates Api").click();

    cy.wait("@getSpecifications");

    cy.get("input[name='connectionConfiguration.base']").type("USD");
    cy.get("input[name='connectionConfiguration.start_date']").type("2020-12-12");

    cy.get("button[type=submit]").click();
    cy.wait("@checkConnection");
    cy.wait("@createSource");
    cy.wait(3000);

    cy.get("div[role=combobox]").click();
    cy.get("div[data-id='create-new-item']").click();
    cy.wait("@checkConnectionSource");

    cy.get("input[name=name]").type("Test destination cypress");
    cy.get("div[role=combobox]").click();
    cy.get("div").contains("Local JSON").click();

    cy.wait("@getSpecificationsDestination");

    cy.get("input[name='connectionConfiguration.destination_path']").type("/local");

    cy.get("button[type=submit]").click();

    cy.wait("@checkConnectionDestination");
    cy.wait("@createDestination");
    cy.wait("@discoverSchema");

    cy.get("div[role=combobox]").last().click();
    cy.get("div[data-id='manual']").click();
    cy.get("button[type=submit]").click();

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
    cy.get("button[type=submit]").click();
    cy.wait("@updateConnection");
    cy.get("span[data-id='success-result']").should("exist");

    cy.get("div[data-id='status-step']").click();
    cy.get("div").contains("5 min").should("exist");
});

  it("Delete connection", () => {
    cy.get("div").contains("Test source cypress").click();
    cy.get("div").contains("Test destination cypress").click();

    cy.get("div[data-id='settings-step']").click();
    cy.get("button[data-id='open-delete-modal']").click();
    cy.get("button[data-id='delete']").click();

    cy.visit("/");

    cy.get("div").contains("Test source cypress").click();
    cy.get("div[data-id='settings-step']").click();
    cy.get("button[data-id='open-delete-modal']").click();
    cy.get("button[data-id='delete']").click();

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress").click();
    cy.get("div[data-id='settings-step']").click();
    cy.get("button[data-id='open-delete-modal']").click();
    cy.get("button[data-id='delete']").click();
  });
});
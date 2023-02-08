export const interceptGetConnectionRequest = () =>
  cy.intercept("/api/v1/web_backend/connections/get").as("getConnection");
export const waitForGetConnectionRequest = () => cy.wait("@getConnection");

export const interceptUpdateConnectionRequest = () =>
  cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");
export const waitForUpdateConnectionRequest = () => cy.wait("@updateConnection", { timeout: 10000 });

export const interceptDiscoverSchemaRequest = () =>
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
export const waitForDiscoverSchemaRequest = () => cy.wait("@discoverSchema");

export const interceptCreateConnectionRequest = () =>
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");
export const waitForCreateConnectionRequest = () => cy.wait("@createConnection");

export const interceptGetSourcesListRequest = () => cy.intercept("/api/v1/sources/list").as("getSourcesList");
export const waitForGetSourcesListRequest = () => cy.wait("@getSourcesList");

export const interceptGetSourceDefinitionsRequest = () =>
  cy.intercept("/api/v1/source_definitions/list_for_workspace").as("getSourceDefinitions");
export const waitForGetSourceDefinitionsRequest = () => cy.wait("@getSourceDefinitions");

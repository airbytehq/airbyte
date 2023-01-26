export const interceptGetConnectionRequest = () => cy.intercept("/api/v1/web_backend/connections/get").as("getConnection")
export const waitForGetConnectionRequest = () => cy.wait("@getConnection");

export const interceptUpdateConnectionRequest = () =>
  cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");
export const waitForUpdateConnectionRequest = () => cy.wait("@updateConnection", { timeout: 10000 });

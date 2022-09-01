export const submitButtonClick = () => {
  cy.get("button[type=submit]").click();
}

export const updateField = (field: string, value: string) => {
  cy.get("input[name='" + field + "']").clear().type(value);
}

export const openSettingForm = (name: string) => {
  cy.get("div").contains(name).click();
  cy.get("div[data-id='settings-step']").click();
}

export const deleteEntity = () => {
  cy.get("button[data-id='open-delete-modal']").click();
  cy.get("button[data-id='delete']").click();
}

export const clearApp = () => {
  indexedDB.deleteDatabase("firebaseLocalStorageDb");
  cy.clearLocalStorage();
  cy.clearCookies();
}

export const fillEmail = (email: string) => {
  cy.get("input[name=email]").type(email);
}

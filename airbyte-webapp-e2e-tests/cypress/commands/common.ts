export const submitButtonClick = () => {
  cy.get("button[type=submit]").click();
};

export const updateField = (field: string, value: string) => {
  cy.get(`input[name='${field}']`).clear().type(value);
};

export const openSettingForm = (name: string) => {
  cy.get("div").contains(name).click();
  cy.get("div[data-id='settings-step']").click();
};

export const deleteEntity = () => {
  cy.get("button[data-id='open-delete-modal']").click();
  cy.get("button[data-id='delete']").click();
};

export const clearApp = () => {
  indexedDB.deleteDatabase("firebaseLocalStorageDb");
  cy.clearLocalStorage();
  cy.clearCookies();
};

export const fillEmail = (email: string) => {
  cy.get("input[name=email]").type(email);
};

// useful for ensuring that a name is unique from one test run to the next
export const appendRandomString = (string: string) => {
  const randomString = Math.random().toString(36).substring(2, 10);
  return `${string} _${randomString}`;
};

/**
 * Click on specific cell found by column name in desired table
 * @param tableSelector - table selector
 * @param columnName - column name
 * @param connectName - cell text
 */
export const clickOnCellInTable = (tableSelector: string, columnName: string, connectName: string) => {
  cy.contains(`${tableSelector} th`, columnName)
    .invoke("index")
    .then((value) => {
      cy.log(`${value}`);
      return cy.wrap(value);
    })
    .then((columnIndex) => {
      cy.contains("tbody tr", connectName).find("td").eq(columnIndex).click();
    });
};

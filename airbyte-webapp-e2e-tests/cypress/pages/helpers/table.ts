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

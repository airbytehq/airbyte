const refreshSourceSchemaButton = "button[data-testid='refresh-source-schema-btn']";
const streamNameInput = "input[data-testid='input']";

export class StreamsTablePageObjectBase {
  refreshSourceSchemaBtnClick() {
    cy.get(refreshSourceSchemaButton).click();
  }

  searchStream(value: string) {
    cy.get(streamNameInput).type(value);
  }

  clearStreamSearch() {
    cy.get(streamNameInput).clear();
  }
}

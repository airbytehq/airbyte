const refreshSourceSchemaButton = "button[data-testid='refresh-source-schema-btn']";
const streamNameInput = "input[data-testid='input']";

export abstract class AbstractStreamsTablePageObject {
  abstract expandStreamDetailsByName(streamName: string): void;
  abstract selectSyncMode(source: string, dest: string): void;
  abstract selectCursorField(streamName: string, cursorValue: string): void;
  abstract selectPrimaryKeyField(streamName: string, primaryKeyValues: string[]): void;
  abstract checkStreamFields(listNames: string[], listTypes: string[]): void;
  abstract checkCursorField(streamName: string, expectedValue: string): void;
  abstract checkPrimaryKey(streamName: string, expectedValues: string[]): void;
  abstract checkPreFilledPrimaryKeyField(streamName: string, expectedValue: string): void;
  abstract isPrimaryKeyNonExist(streamName: string): void;
  abstract toggleStreamEnabledState(streamName: string): void;

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

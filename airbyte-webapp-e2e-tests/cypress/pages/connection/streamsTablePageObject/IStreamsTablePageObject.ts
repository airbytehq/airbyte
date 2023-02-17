export interface IStreamsTablePageObject {
  expandStreamDetailsByName(streamName: string): void;
  selectSyncMode(source: string, dest: string): void;
  selectCursorField(streamName: string, cursorValue: string): void;
  selectPrimaryKeyField(streamName: string, primaryKeyValues: string[]): void;
  checkStreamFields(listNames: string[], listTypes: string[]): void;
  checkCursorField(streamName: string, expectedValue: string): void;
  checkPrimaryKey(streamName: string, expectedValues: string[]): void;
  checkPreFilledPrimaryKeyField(streamName: string, expectedValue: string): void;
  isPrimaryKeyNonExist(streamName: string): void;
  toggleStreamEnabledState(streamName: string): void;
}

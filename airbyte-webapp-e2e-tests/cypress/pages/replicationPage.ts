const scheduleDropdown = "div[data-testid='scheduleData']";
const scheduleValue = (value: string) => `div[data-testid='${value}']`;
const destinationPrefix = "input[data-testid='prefixInput']";
const replicationTab = "div[data-id='replication-step']";
const destinationNamespace = "div[data-testid='namespaceDefinition']";
const destinationNamespaceCustom = "div[data-testid='namespaceDefinition-customformat']";
const destinationNamespaceDefault = "div[data-testid='namespaceDefinition-destination']";
const destinationNamespaceSource = "div[data-testid='namespaceDefinition-source']";
const destinationNamespaceCustomInput = "input[data-testid='input']";
const syncModeDropdown = "div[data-testid='syncSettingsDropdown'] input";
const getFieldDropdownContainer = (streamName: string, type: Dropdown) => `div[id='${streamName}_${type}_pathPopout']`;
const getFieldDropdownButton = (streamName: string, type: Dropdown) =>
  `button[data-testid='${streamName}_${type}_pathPopout']`;
const getFieldDropdownOption = (value: string) => `div[data-testid='${value}']`;
const dropDownOverlayContainer = "div[data-testid='overlayContainer']";
const streamNameCell = "[data-testid='nameCell']";
const streamDataTypeCell = "[data-testid='dataTypeCell']";
const getExpandStreamArrowBtn = (streamName: string) => `[data-testid='${streamName}_expandStreamDetails']`;
const getPreFilledPrimaryKeyText = (streamName: string) => `[data-testid='${streamName}_primaryKey_pathPopout_text']`;
const successResult = "div[data-id='success-result']";
const saveStreamChangesButton = "button[data-testid='resetModal-save']";
const connectionNameInput = "input[data-testid='connectionName']";
const refreshSourceSchemaButton = "button[data-testid='refresh-source-schema-btn']";
const streamSyncEnabledSwitch = (streamName: string) => `[data-testid='${streamName}-stream-sync-switch']`;
const streamNameInput = "input[data-testid='input']";
const resetModalSaveButton = "[data-testid='resetModal-save']";

export const goToReplicationTab = () => {
  cy.get(replicationTab).click();
};

export const enterConnectionName = (name: string) => {
  cy.get(connectionNameInput).type(name);
};

export const expandStreamDetailsByName = (streamName: string) => cy.get(getExpandStreamArrowBtn(streamName)).click();

export const selectSchedule = (value: string) => {
  cy.get(scheduleDropdown).click();
  cy.get(scheduleValue(value)).click();
};

export const fillOutDestinationPrefix = (value: string) => {
  cy.get(destinationPrefix).clear().type(value).should("have.value", value);
};

export const setupDestinationNamespaceCustomFormat = (value: string) => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceCustom).click();
  cy.get(destinationNamespaceCustomInput).first().type(value).should("have.value", `\${SOURCE_NAMESPACE}${value}`);
};

export const setupDestinationNamespaceSourceFormat = () => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceSource).click();
};

export const refreshSourceSchemaBtnClick = () => cy.get(refreshSourceSchemaButton).click();

export const resetModalSaveBtnClick = () => cy.get(resetModalSaveButton).click();

export const setupDestinationNamespaceDefaultFormat = () => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceDefault).click();
};

export const selectSyncMode = (source: string, dest: string) => {
  cy.get(syncModeDropdown).first().click({ force: true });

  cy.get(`.react-select__option`).contains(`Source:${source}|Dest:${dest}`).click();
};

type Dropdown = "cursor" | "primaryKey";
/**
 * General function - select dropdown option(s)
 * @param streamName
 * @param dropdownType
 * @param value
 */
const selectFieldDropdownOption = (streamName: string, dropdownType: Dropdown, value: string | string[]) => {
  const container = getFieldDropdownContainer(streamName, dropdownType);
  const button = getFieldDropdownButton(streamName, dropdownType);

  cy.get(container).within(() => {
    cy.get(button).click();

    if (Array.isArray(value)) {
      // in case if multiple options need to be selected
      value.forEach((v) => cy.get(getFieldDropdownOption(v)).click());
    } else {
      // in case if one option need to be selected
      cy.get(getFieldDropdownOption(value)).click();
    }
  });
  // close dropdown
  // (dropdown need to be closed manually by clicking on overlay in case if multiple option selection is available)
  cy.get("body").then(($body) => {
    if ($body.find(dropDownOverlayContainer).length > 0) {
      cy.get(dropDownOverlayContainer).click();
    }
  });
};

/**
 * Select cursor value from cursor dropdown(pathPopout) in desired stream
 * @param streamName
 * @param cursorValue
 */
export const selectCursorField = (streamName: string, cursorValue: string) =>
  selectFieldDropdownOption(streamName, "cursor", cursorValue);

/**
 * Select primary key value(s) from primary key dropdown(pathPopout) in desired stream
 * @param streamName
 * @param primaryKeyValues
 */
export const selectPrimaryKeyField = (streamName: string, primaryKeyValues: string[]) =>
  selectFieldDropdownOption(streamName, "primaryKey", primaryKeyValues);

export const checkStreamFields = (listNames: Array<String>, listTypes: Array<String>) => {
  cy.get(streamNameCell).each(($span, i) => {
    expect($span.text()).to.equal(listNames[i]);
  });

  cy.get(streamDataTypeCell).each(($span, i) => {
    expect($span.text()).to.equal(listTypes[i]);
  });
};

/**
 * General function - check selected field dropdown option or options
 * @param streamName
 * @param dropdownType
 * @param expectedValue
 */
const checkDropdownField = (streamName: string, dropdownType: Dropdown, expectedValue: string | string[]) => {
  const button = getFieldDropdownButton(streamName, dropdownType);
  const isButtonContainsExactValue = (value: string) => cy.get(button).contains(new RegExp(`^${value}$`));

  return Array.isArray(expectedValue)
    ? expectedValue.every((value) => isButtonContainsExactValue(value))
    : isButtonContainsExactValue(expectedValue);
};

/**
 * Check selected value in cursor dropdown
 * @param streamName
 * @param expectedValue
 */
export const checkCursorField = (streamName: string, expectedValue: string) =>
  checkDropdownField(streamName, "cursor", expectedValue);

/**
 * Check selected value(s) in primary key dropdown
 * @param streamName
 * @param expectedValues
 */
export const checkPrimaryKey = (streamName: string, expectedValues: string[]) =>
  checkDropdownField(streamName, "primaryKey", expectedValues);

export const checkPreFilledPrimaryKeyField = (streamName: string, expectedValue: string) => {
  cy.get(getPreFilledPrimaryKeyText(streamName)).contains(expectedValue);
};

export const isPrimaryKeyNonExist = (streamName: string) => {
  cy.get(getPreFilledPrimaryKeyText(streamName)).should("not.exist");
};

export const searchStream = (value: string) => {
  cy.get(streamNameInput).type(value);
};

export const checkSuccessResult = () => {
  cy.get(successResult).should("exist");
};

export const confirmStreamConfigurationChangedPopup = () => {
  cy.get(saveStreamChangesButton).click();
};

export const toggleStreamEnabledState = (streamName: string) => {
  cy.get(streamSyncEnabledSwitch(streamName)).check({ force: true });
};

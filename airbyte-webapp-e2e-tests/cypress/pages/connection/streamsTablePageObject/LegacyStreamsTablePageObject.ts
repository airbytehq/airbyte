import { IStreamsTablePageObject } from "./IStreamsTablePageObject";
import { StreamsTablePageObjectBase } from "./StreamsTableContainerPageObject";

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
const streamSyncEnabledSwitch = (streamName: string) => `[data-testid='${streamName}-stream-sync-switch']`;

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

export class LegacyStreamsTablePageObject extends StreamsTablePageObjectBase implements IStreamsTablePageObject {
  expandStreamDetailsByName(streamName: string) {
    cy.get(getExpandStreamArrowBtn(streamName)).click();
  }

  selectSyncMode(source: string, dest: string) {
    cy.get(syncModeDropdown).first().click({ force: true });

    cy.get(`.react-select__option`).contains(`Source:${source}|Dest:${dest}`).click();
  }

  /**
   * Select cursor value from cursor dropdown(pathPopout) in desired stream
   * @param streamName
   * @param cursorValue
   */
  selectCursorField(streamName: string, cursorValue: string) {
    selectFieldDropdownOption(streamName, "cursor", cursorValue);
  }

  /**
   * Select primary key value(s) from primary key dropdown(pathPopout) in desired stream
   * @param streamName
   * @param primaryKeyValues
   */
  selectPrimaryKeyField(streamName: string, primaryKeyValues: string[]) {
    selectFieldDropdownOption(streamName, "primaryKey", primaryKeyValues);
  }

  checkStreamFields(listNames: string[], listTypes: string[]) {
    cy.get(streamNameCell).each(($span, i) => {
      expect($span.text()).to.equal(listNames[i]);
    });

    cy.get(streamDataTypeCell).each(($span, i) => {
      expect($span.text()).to.equal(listTypes[i]);
    });
  }

  /**
   * Check selected value in cursor dropdown
   * @param streamName
   * @param expectedValue
   */
  checkCursorField(streamName: string, expectedValue: string) {
    checkDropdownField(streamName, "cursor", expectedValue);
  }

  /**
   * Check selected value(s) in primary key dropdown
   * @param streamName
   * @param expectedValues
   */
  checkPrimaryKey(streamName: string, expectedValues: string[]) {
    checkDropdownField(streamName, "primaryKey", expectedValues);
  }

  checkPreFilledPrimaryKeyField(streamName: string, expectedValue: string) {
    cy.get(getPreFilledPrimaryKeyText(streamName)).contains(expectedValue);
  }

  isPrimaryKeyNonExist(streamName: string) {
    cy.get(getPreFilledPrimaryKeyText(streamName)).should("not.exist");
  }

  toggleStreamEnabledState(streamName: string) {
    cy.get(streamSyncEnabledSwitch(streamName)).check({ force: true });
  }
}

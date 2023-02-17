import { submitButtonClick } from "commands/common";

const resetModalSaveButton = "[data-testid='resetModal-save']";
const successResult = "div[data-id='success-result']";
const resetModalResetCheckbox = "[data-testid='resetModal-reset-checkbox']";
const saveStreamChangesButton = "button[data-testid='resetModal-save']";
const schemaChangesDetectedBanner = "[data-testid='schemaChangesDetected']";
const schemaChangesReviewButton = "[data-testid='schemaChangesReviewButton']";
const schemaChangesBackdrop = "[data-testid='schemaChangesBackdrop']";
const nonBreakingChangesPreference = "[data-testid='nonBreakingChangesPreference']";
const nonBreakingChangesPreferenceValue = (value: string) => `div[data-testid='nonBreakingChangesPreference-${value}']`;
const noDiffToast = "[data-testid='notification-connection.noDiff']";

export const checkSchemaChangesDetected = ({ breaking }: { breaking: boolean }) => {
  cy.get(schemaChangesDetectedBanner).should("exist");
  cy.get(schemaChangesDetectedBanner)
    .invoke("attr", "class")
    .should("match", breaking ? /\_breaking/ : /nonBreaking/);
  cy.get(schemaChangesBackdrop).should(breaking ? "exist" : "not.exist");
};

export const clickSaveButton = ({ reset = false, confirm = true } = {}) => {
  cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

  submitButtonClick();

  if (confirm) {
    confirmStreamConfigurationChangedPopup({ reset });
  }

  cy.wait("@updateConnection").then((interception) => {
    assert.isNotNull(interception.response?.statusCode, "200");
  });

  checkSuccessResult();
};

export const checkSuccessResult = () => {
  cy.get(successResult).should("exist");
};

export const confirmStreamConfigurationChangedPopup = ({ reset = false } = {}) => {
  if (!reset) {
    cy.get(resetModalResetCheckbox).click({ force: true });
  }
  cy.get(saveStreamChangesButton).click();
};

export const checkSchemaChangesDetectedCleared = () => {
  cy.get(schemaChangesDetectedBanner).should("not.exist");
  cy.get(schemaChangesBackdrop).should("not.exist");
};

export const checkNoDiffToast = () => {
  cy.get(noDiffToast).should("exist");
};

export const clickSchemaChangesReviewButton = () => {
  cy.get(schemaChangesReviewButton).click();
  cy.get(schemaChangesReviewButton).should("be.disabled");
};

export const selectNonBreakingChangesPreference = (preference: "ignore" | "disable") => {
  cy.get(nonBreakingChangesPreference).click();
  cy.get(nonBreakingChangesPreferenceValue(preference)).click();
};

export const resetModalSaveBtnClick = () => cy.get(resetModalSaveButton).click();

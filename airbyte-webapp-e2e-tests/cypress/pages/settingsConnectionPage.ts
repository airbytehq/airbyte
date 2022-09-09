const settingsTab = "div[data-id='settings-step']";

export const goToSettingsPage = () => {
    cy.get(settingsTab).click();
}

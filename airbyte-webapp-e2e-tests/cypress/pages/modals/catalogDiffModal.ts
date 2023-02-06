export const catalogDiffModal = "[data-testid='catalog-diff-modal']";
export const removedStreamsTable = "table[aria-label='removed streams table']";
export const newStreamsTable = "table[aria-label='new streams table']";
const streamWithChangesToggleBtn = (streamName: string) =>
  `button[data-testid='toggle-accordion-${streamName}-stream']`;
export const removedFieldsTable = "table[aria-label='removed fields']";
export const newFieldsTable = "table[aria-label='new fields']";
export const closeButton = "[data-testid='update-schema-confirm-btn']";

export const checkCatalogDiffModal = () => {
  cy.get(catalogDiffModal).should("exist");
};

export const toggleStreamWithChangesAccordion = (streamName: string) => {
  cy.get(streamWithChangesToggleBtn(streamName)).click();
};

export const clickCatalogDiffCloseButton = () => {
  cy.get(closeButton).click();
};

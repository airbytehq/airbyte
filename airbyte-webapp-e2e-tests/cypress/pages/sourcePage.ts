export const goToSourcePage = () => {
    cy.visit("/source");
}

export const openSourceDestinationFromGrid = (value: string) => {
    cy.get("div").contains(value).click();
}

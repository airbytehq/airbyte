const emailInput = "input[name=email]";

export const fillEmail = (email: string) => {
    cy.get(emailInput).type(email);
}
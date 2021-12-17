import { parse } from "node-html-parser";

Cypress.Commands.add("fillEmail", (email) => {
  cy.get("input[name=email]").type(email);
});

Cypress.Commands.add("fillPassword", (password) => {
  cy.get("input[name=password]").type(password);
});

Cypress.Commands.add("fillSignInForm", (email) => {
  cy.fillEmail(email);
  cy.fillPassword(email);
});

Cypress.Commands.add("fillSignUpForm", (email) => {
  cy.fillSignInForm(email);

  cy.get("input[name=name]").type(email);
  cy.get("input[name=company]").type(email);
  cy.get("input[name=security]").click();
});

Cypress.Commands.add("selectWorkspaceAfterLogin", () => {
  cy.wait(1000);
  cy.get("h5").first().click();
  cy.wait(5000);
});

Cypress.Commands.add("signUp", (onDone = () => {}) => {
  cy.visit("/signup");

  cy.createInbox().then((inbox) => {
    cy.fillSignUpForm(inbox.emailAddress);
    cy.get("button[type=submit]").click();

    cy.waitForLatestEmail(inbox.id).then((email) => {
      cy.visitConfirmationLink(email.body);
      cy.selectWorkspaceAfterLogin();

      onDone(inbox.emailAddress, inbox.id);
    });
  });
});

Cypress.Commands.add("signIn", (email) => {
  cy.visit("/login");
  cy.fillSignInForm(email);
  cy.get("button[type=submit]").click();
  cy.selectWorkspaceAfterLogin();
});

Cypress.Commands.add("signOut", () => {
  cy.openSettings();
  cy.get("button[data-testid='button.signout']").click();
});

Cypress.Commands.add("visitConfirmationLink", (src) => {
  cy.wait(1000);
  const root = parse(`<div>${src}</div>`);
  const url = root.querySelector("a").getAttribute("href");

  cy.visit(url);
  cy.wait(2500);
});

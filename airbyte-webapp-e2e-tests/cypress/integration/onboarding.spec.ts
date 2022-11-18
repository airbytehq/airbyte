import { submitButtonClick, fillEmail } from "commands/common";
import { initialSetupCompleted } from "commands/workspaces";

describe("Preferences actions", () => {
  beforeEach(() => {
    initialSetupCompleted(false);
  });

  it("Should redirect to connections page after email is entered", () => {
    cy.visit("/preferences");
    cy.url().should("include", `/preferences`);

    fillEmail("test-email-onboarding@test-onboarding-domain.com");
    cy.get("input[name=securityUpdates]").parent().click();

    submitButtonClick();

    cy.url().should("match", /.*\/connections/);
  });
});

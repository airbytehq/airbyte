import { deleteEntity } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";

describe("Connection main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new connection", () => {
    createTestConnection("Test connection source cypress", "Test destination cypress");

    cy.get("div").contains("Test connection source cypress").should("exist");
    cy.get("div").contains("Test destination cypress").should("exist");
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    createTestConnection("Test update connection source cypress", "Test update connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test update connection source cypress").click();
    cy.get("div").contains("Test update connection destination cypress").click();

    cy.get("div[data-id='replication-step']").click();

    cy.get("div[data-testid='scheduleData.basicSchedule']").click();
    cy.get("div[data-testid='Every hour']").click();
    cy.get("input[data-testid='prefixInput']").clear();
    cy.get("input[data-testid='prefixInput']").type('auto_test');
    cy.get("button[type=submit]").first().click();
    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, '200');
    cy.get("span[data-id='success-result']").should("exist");


    })
});

it("Update connection (pokeAPI)", () => {
  cy.intercept({
    method: "POST",
    url: "/api/v1/web_backend/connections/updateNew"}).as("updateConnection");

  //createTestConnection("Test update connection PokeAPI source cypress", "Test update connection destination cypress");

  cy.visit("/source");
  cy.get("div").contains("Test update connection PokeAPI source cypress").click();
  cy.get("div").contains("Test update connection destination cypress").click();

  cy.get("div[data-id='replication-step']").click();

  cy.get("div[data-testid='schedule']").click();
  cy.get("div[data-testid='Every 5 minutes']").click();
  cy.get("input[data-testid='prefixInput']").clear().type('auto_test');
  cy.get("div.sc-jgbSNz.sc-gSAPjG.dmcQNW.kFkHkC.SyncCatalogField_catalogHeader__vtJPc input.sc-jSMfEi.dZkanq").check({force: true});
  //cy.get("div.sc-iBkjds.eXsTY").first().select('Full refresh | Append');
  cy.get("button[type=submit]").first().click();

  cy.wait("@updateConnection").then((interception) => {
    assert.isNotNull(interception.response?.statusCode, '200');
    expect(interception.request.method).to.eq('POST');
    cy.log(interception.request.body);
    expect(interception.request).property('body').to.contain({
      name: 'Test update connection PokeAPI source cypress <> Test update connection destination cypress',
      prefix: 'auto_test',
      shedule: {
        units: 5,
        timeUnit: 'minutes'
      }
    })
    
  })
  cy.get("span[data-id='success-result']").should("exist");
});

  it("Delete connection", () => {
    createTestConnection("Test delete connection source cypress", "Test delete connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test delete connection source cypress").click();
    cy.get("div").contains("Test delete connection destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    deleteEntity();

    deleteSource("Test delete connection source cypress");
    deleteDestination("Test delete connection destination cypress");
  });
});
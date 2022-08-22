import { deleteEntity } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import { confirmStreamConfigurationChangedPopup, clickSaveChanges, selectSchedule, fillOutDestinationPrefix, goToReplicationTab, setupDestinationNamespaceCustomFormat, selectFullAppendSyncMode, checkSuccessResult} from "pages/replicationPage";
import { openSourceDestinationFromGrid, goToSourcePage} from "pages/sourcePage";

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

    createTestConnection("Test update connection PokeAPI source cypress", "Test update connection Local JSON destination cypress");

    goToSourcePage();
    openSourceDestinationFromGrid("Test update connection PokeAPI source cypress");
    openSourceDestinationFromGrid("Test update connection Local JSON destination cypress");

    goToReplicationTab();

    selectSchedule('Every 5 minutes');
    fillOutDestinationPrefix('auto_test');
    setupDestinationNamespaceCustomFormat('_test');
    selectFullAppendSyncMode();

    clickSaveChanges();
    confirmStreamConfigurationChangedPopup();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, '200');
      expect(interception.request.method).to.eq('POST');
      expect(interception.request).property('body').to.contain({
        name: 'Test update connection PokeAPI source cypress <> Test update connection Local JSON destination cypressConnection name',
        prefix: 'auto_test',
        namespaceDefinition: 'customformat',
        namespaceFormat: '${SOURCE_NAMESPACE}_test',
        status: 'active',
      });
      expect(interception.request.body.schedule).to.contain({
        units: 5,
        timeUnit: 'minutes'
      });

      expect(interception.request.body.syncCatalog.streams[0].config).to.contain({
        aliasName: 'pokemon',
        destinationSyncMode: 'append',
        selected: true,
      });

      expect(interception.request.body.syncCatalog.streams[0].stream).to.contain({
        name: "pokemon",
      });
      expect(interception.request.body.syncCatalog.streams[0].stream.supportedSyncModes).to.contain(
        'full_refresh'
      );
    })
    checkSuccessResult();
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
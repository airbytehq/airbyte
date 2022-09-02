import { deleteEntity, submitButtonClick } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import { confirmStreamConfigurationChangedPopup, selectSchedule, fillOutDestinationPrefix, goToReplicationTab, setupDestinationNamespaceCustomFormat, selectFullAppendSyncMode, checkSuccessResult} from "pages/replicationPage";
import { openSourceDestinationFromGrid, goToSourcePage} from "pages/sourcePage";
import { goToSettingsPage } from "pages/settingsConnectionPage"

describe("Connection main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new connection", () => {
    createTestConnection("Test connection source cypress", "Test connection destination cypress");

    cy.get("div").contains("Test connection source cypress").should("exist");
    cy.get("div").contains("Test connection destination cypress").should("exist");

    deleteSource("Test connection source cypress");
    deleteDestination("Test connection destination cypress");
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    createTestConnection("Test update connection source cypress", "Test update connection destination cypress");

    goToSourcePage();
    openSourceDestinationFromGrid("Test update connection source cypress");
    openSourceDestinationFromGrid("Test update connection destination cypress");

    goToReplicationTab();

    selectSchedule('Every hour');
    fillOutDestinationPrefix('auto_test');

    submitButtonClick();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, '200');    
    });

    checkSuccessResult();

    deleteSource("Test update connection source cypress");
    deleteDestination("Test update connection destination cypress");
  });

  it("Update connection (pokeAPI)", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    createTestConnection("Test update connection PokeAPI source cypress", "Test update connection Local JSON destination cypress");

    goToSourcePage();
    openSourceDestinationFromGrid("Test update connection PokeAPI source cypress");
    openSourceDestinationFromGrid("Test update connection Local JSON destination cypress");

    goToReplicationTab();

    selectSchedule('Every hour');
    fillOutDestinationPrefix('auto_test');
    setupDestinationNamespaceCustomFormat('_test');
    selectFullAppendSyncMode();

    submitButtonClick();
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
      expect(interception.request.body.scheduleData.basicSchedule).to.contain({
        units: 1,
        timeUnit: 'hours'
      });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.config).to.contain({
        aliasName: 'pokemon',
        destinationSyncMode: 'append',
        selected: true,
      });

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
      expect(streamToUpdate.stream.supportedSyncModes).to.contain(
        'full_refresh'
      );
    })
    checkSuccessResult();

    deleteSource("Test update connection PokeAPI source cypress");
    deleteDestination("Test update connection Local JSON destination cypress");
  });

  it("Delete connection", () => {
    createTestConnection("Test delete connection source cypress", "Test delete connection destination cypress");

    goToSourcePage();
    openSourceDestinationFromGrid("Test delete connection source cypress");
    openSourceDestinationFromGrid("Test delete connection destination cypress");

    goToSettingsPage();

    deleteEntity();

    deleteSource("Test delete connection source cypress");
    deleteDestination("Test delete connection destination cypress");
  });
});
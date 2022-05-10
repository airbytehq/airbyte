/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DatabaseConfigPersistenceE2EReadWriteTest extends BaseDatabaseConfigPersistenceTest {

  @BeforeEach
  public void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    database = new ConfigsDatabaseInstance(dslContext).getAndInitialize();
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceLoadDataTest.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);

    configPersistence = spy(new DatabaseConfigPersistence(database, jsonSecretsProcessor));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, flyway);
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
    truncateAllTables();
  }

  @AfterEach
  void tearDown() throws IOException {
    dslContext.close();
    if (dataSource instanceof Closeable closeable) {
      closeable.close();
    }
  }

  @Test
  public void test() throws JsonValidationException, IOException, ConfigNotFoundException {
    standardWorkspace();
    standardSourceDefinition();
    standardDestinationDefinition();
    sourceConnection();
    destinationConnection();
    sourceOauthParam();
    destinationOauthParam();
    standardSyncOperation();
    standardSync();
    standardSyncState();
    standardActorCatalog();
    workspaceServiceAccounts();
    deletion();
  }

  private void deletion() throws ConfigNotFoundException, IOException, JsonValidationException {
    // Deleting the workspace should delete everything except for definitions and catalogs
    for (final StandardWorkspace standardWorkspace : MockData.standardWorkspaces()) {
      configPersistence.deleteConfig(ConfigSchema.STANDARD_WORKSPACE, standardWorkspace.getWorkspaceId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC_STATE, StandardSyncState.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC_OPERATION, StandardSyncOperation.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, SourceConnection.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT, ActorCatalogFetchEvent.class).isEmpty());
    assertTrue(configPersistence.listConfigs(ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, ActorCatalogFetchEvent.class).isEmpty());

    assertFalse(configPersistence.listConfigs(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.class).isEmpty());
    assertFalse(configPersistence.listConfigs(ConfigSchema.DESTINATION_OAUTH_PARAM, DestinationOAuthParameter.class).isEmpty());
    assertFalse(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class).isEmpty());
    assertFalse(configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class).isEmpty());
    assertFalse(configPersistence.listConfigs(ConfigSchema.ACTOR_CATALOG, ActorCatalog.class).isEmpty());

    for (final SourceOAuthParameter sourceOAuthParameter : MockData.sourceOauthParameters()) {
      configPersistence.deleteConfig(ConfigSchema.SOURCE_OAUTH_PARAM, sourceOAuthParameter.getOauthParameterId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.class).isEmpty());

    for (final DestinationOAuthParameter destinationOAuthParameter : MockData.destinationOauthParameters()) {
      configPersistence.deleteConfig(ConfigSchema.DESTINATION_OAUTH_PARAM, destinationOAuthParameter.getOauthParameterId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.DESTINATION_OAUTH_PARAM, DestinationOAuthParameter.class).isEmpty());

    for (final StandardSourceDefinition standardSourceDefinition : MockData.standardSourceDefinitions()) {
      configPersistence.deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, standardSourceDefinition.getSourceDefinitionId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class).isEmpty());

    for (final StandardDestinationDefinition standardDestinationDefinition : MockData.standardDestinationDefinitions()) {
      configPersistence
          .deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, standardDestinationDefinition.getDestinationDefinitionId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class).isEmpty());

    for (final ActorCatalog actorCatalog : MockData.actorCatalogs()) {
      configPersistence
          .deleteConfig(ConfigSchema.ACTOR_CATALOG, actorCatalog.getId().toString());
    }
    assertTrue(configPersistence.listConfigs(ConfigSchema.ACTOR_CATALOG, ActorCatalog.class).isEmpty());
  }

  private void standardSyncState() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardSyncState standardSyncState : MockData.standardSyncStates()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC_STATE,
          standardSyncState.getConnectionId().toString(),
          standardSyncState);
      final StandardSyncState standardSyncStateFromDB = configPersistence.getConfig(ConfigSchema.STANDARD_SYNC_STATE,
          standardSyncState.getConnectionId().toString(),
          StandardSyncState.class);
      assertEquals(standardSyncState, standardSyncStateFromDB);
    }
    final List<StandardSyncState> standardSyncStates = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SYNC_STATE, StandardSyncState.class);
    assertEquals(MockData.standardSyncStates().size(), standardSyncStates.size());
    assertThat(MockData.standardSyncStates()).hasSameElementsAs(standardSyncStates);
  }

  private void standardSync() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardSync standardSync : MockData.standardSyncs()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC,
          standardSync.getConnectionId().toString(),
          standardSync);
      final StandardSync standardSyncFromDB = configPersistence.getConfig(ConfigSchema.STANDARD_SYNC,
          standardSync.getConnectionId().toString(),
          StandardSync.class);
      assertEquals(standardSync, standardSyncFromDB);
    }
    final List<StandardSync> standardSyncs = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
    assertEquals(MockData.standardSyncs().size(), standardSyncs.size());
    assertThat(MockData.standardSyncs()).hasSameElementsAs(standardSyncs);
  }

  private void standardSyncOperation() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardSyncOperation standardSyncOperation : MockData.standardSyncOperations()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC_OPERATION,
          standardSyncOperation.getOperationId().toString(),
          standardSyncOperation);
      final StandardSyncOperation standardSyncOperationFromDB = configPersistence.getConfig(ConfigSchema.STANDARD_SYNC_OPERATION,
          standardSyncOperation.getOperationId().toString(),
          StandardSyncOperation.class);
      assertEquals(standardSyncOperation, standardSyncOperationFromDB);
    }
    final List<StandardSyncOperation> standardSyncOperations = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SYNC_OPERATION, StandardSyncOperation.class);
    assertEquals(MockData.standardSyncOperations().size(), standardSyncOperations.size());
    assertThat(MockData.standardSyncOperations()).hasSameElementsAs(standardSyncOperations);
  }

  private void destinationOauthParam() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final DestinationOAuthParameter destinationOAuthParameter : MockData.destinationOauthParameters()) {
      configPersistence.writeConfig(ConfigSchema.DESTINATION_OAUTH_PARAM,
          destinationOAuthParameter.getOauthParameterId().toString(),
          destinationOAuthParameter);
      final DestinationOAuthParameter destinationOAuthParameterFromDB = configPersistence.getConfig(ConfigSchema.DESTINATION_OAUTH_PARAM,
          destinationOAuthParameter.getOauthParameterId().toString(),
          DestinationOAuthParameter.class);
      assertEquals(destinationOAuthParameter, destinationOAuthParameterFromDB);
    }
    final List<DestinationOAuthParameter> destinationOAuthParameters = configPersistence
        .listConfigs(ConfigSchema.DESTINATION_OAUTH_PARAM, DestinationOAuthParameter.class);
    assertEquals(MockData.destinationOauthParameters().size(), destinationOAuthParameters.size());
    assertThat(MockData.destinationOauthParameters()).hasSameElementsAs(destinationOAuthParameters);
  }

  private void sourceOauthParam() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final SourceOAuthParameter sourceOAuthParameter : MockData.sourceOauthParameters()) {
      configPersistence.writeConfig(ConfigSchema.SOURCE_OAUTH_PARAM,
          sourceOAuthParameter.getOauthParameterId().toString(),
          sourceOAuthParameter);
      final SourceOAuthParameter sourceOAuthParameterFromDB = configPersistence.getConfig(ConfigSchema.SOURCE_OAUTH_PARAM,
          sourceOAuthParameter.getOauthParameterId().toString(),
          SourceOAuthParameter.class);
      assertEquals(sourceOAuthParameter, sourceOAuthParameterFromDB);
    }
    final List<SourceOAuthParameter> sourceOAuthParameters = configPersistence
        .listConfigs(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.class);
    assertEquals(MockData.sourceOauthParameters().size(), sourceOAuthParameters.size());
    assertThat(MockData.sourceOauthParameters()).hasSameElementsAs(sourceOAuthParameters);
  }

  private void destinationConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final DestinationConnection destinationConnection : MockData.destinationConnections()) {
      configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION,
          destinationConnection.getDestinationId().toString(),
          destinationConnection);
      final DestinationConnection destinationConnectionFromDB = configPersistence.getConfig(ConfigSchema.DESTINATION_CONNECTION,
          destinationConnection.getDestinationId().toString(),
          DestinationConnection.class);
      assertEquals(destinationConnection, destinationConnectionFromDB);
    }
    final List<DestinationConnection> destinationConnections = configPersistence
        .listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
    assertEquals(MockData.destinationConnections().size(), destinationConnections.size());
    assertThat(MockData.destinationConnections()).hasSameElementsAs(destinationConnections);
  }

  private void sourceConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final SourceConnection sourceConnection : MockData.sourceConnections()) {
      configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION,
          sourceConnection.getSourceId().toString(),
          sourceConnection);
      final SourceConnection sourceConnectionFromDB = configPersistence.getConfig(ConfigSchema.SOURCE_CONNECTION,
          sourceConnection.getSourceId().toString(),
          SourceConnection.class);
      assertEquals(sourceConnection, sourceConnectionFromDB);
    }
    final List<SourceConnection> sourceConnections = configPersistence
        .listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
    assertEquals(MockData.sourceConnections().size(), sourceConnections.size());
    assertThat(MockData.sourceConnections()).hasSameElementsAs(sourceConnections);
  }

  private void standardDestinationDefinition() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardDestinationDefinition standardDestinationDefinition : MockData.standardDestinationDefinitions()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION,
          standardDestinationDefinition.getDestinationDefinitionId().toString(),
          standardDestinationDefinition);
      final StandardDestinationDefinition standardDestinationDefinitionFromDB = configPersistence
          .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION,
              standardDestinationDefinition.getDestinationDefinitionId().toString(),
              StandardDestinationDefinition.class);
      assertEquals(standardDestinationDefinition, standardDestinationDefinitionFromDB);
    }
    final List<StandardDestinationDefinition> standardDestinationDefinitions = configPersistence
        .listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
    assertEquals(MockData.standardDestinationDefinitions().size(), standardDestinationDefinitions.size());
    assertThat(MockData.standardDestinationDefinitions()).hasSameElementsAs(standardDestinationDefinitions);
  }

  private void standardSourceDefinition() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardSourceDefinition standardSourceDefinition : MockData.standardSourceDefinitions()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION,
          standardSourceDefinition.getSourceDefinitionId().toString(),
          standardSourceDefinition);
      final StandardSourceDefinition standardSourceDefinitionFromDB = configPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION,
          standardSourceDefinition.getSourceDefinitionId().toString(),
          StandardSourceDefinition.class);
      assertEquals(standardSourceDefinition, standardSourceDefinitionFromDB);
    }
    final List<StandardSourceDefinition> standardSourceDefinitions = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
    assertEquals(MockData.standardSourceDefinitions().size(), standardSourceDefinitions.size());
    assertThat(MockData.standardSourceDefinitions()).hasSameElementsAs(standardSourceDefinitions);
  }

  private void standardWorkspace() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final StandardWorkspace standardWorkspace : MockData.standardWorkspaces()) {
      configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE,
          standardWorkspace.getWorkspaceId().toString(),
          standardWorkspace);
      final StandardWorkspace standardWorkspaceFromDb = configPersistence.getConfig(ConfigSchema.STANDARD_WORKSPACE,
          standardWorkspace.getWorkspaceId().toString(), StandardWorkspace.class);
      assertEquals(standardWorkspace, standardWorkspaceFromDb);
    }
    final List<StandardWorkspace> standardWorkspaces = configPersistence.listConfigs(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class);
    assertEquals(MockData.standardWorkspaces().size(), standardWorkspaces.size());
    assertThat(MockData.standardWorkspaces()).hasSameElementsAs(standardWorkspaces);
  }

  public void standardActorCatalog() throws JsonValidationException, IOException, ConfigNotFoundException {

    for (final ActorCatalog actorCatalog : MockData.actorCatalogs()) {
      configPersistence.writeConfig(ConfigSchema.ACTOR_CATALOG, actorCatalog.getId().toString(), actorCatalog);
      final ActorCatalog retrievedActorCatalog = configPersistence.getConfig(
          ConfigSchema.ACTOR_CATALOG, actorCatalog.getId().toString(), ActorCatalog.class);
      assertEquals(actorCatalog, retrievedActorCatalog);
    } ;
    final List<ActorCatalog> actorCatalogs = configPersistence
        .listConfigs(ConfigSchema.ACTOR_CATALOG, ActorCatalog.class);
    assertEquals(MockData.actorCatalogs().size(), actorCatalogs.size());
    assertThat(MockData.actorCatalogs()).hasSameElementsAs(actorCatalogs);

    for (final ActorCatalogFetchEvent actorCatalogFetchEvent : MockData.actorCatalogFetchEvents()) {
      configPersistence.writeConfig(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT,
          actorCatalogFetchEvent.getId().toString(), actorCatalogFetchEvent);
      final ActorCatalogFetchEvent retrievedActorCatalogFetchEvent = configPersistence.getConfig(
          ConfigSchema.ACTOR_CATALOG_FETCH_EVENT, actorCatalogFetchEvent.getId().toString(),
          ActorCatalogFetchEvent.class);
      assertEquals(actorCatalogFetchEvent, retrievedActorCatalogFetchEvent);
    }
    final List<ActorCatalogFetchEvent> actorCatalogFetchEvents = configPersistence
        .listConfigs(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT, ActorCatalogFetchEvent.class);
    assertEquals(MockData.actorCatalogFetchEvents().size(), actorCatalogFetchEvents.size());
    assertThat(MockData.actorCatalogFetchEvents()).hasSameElementsAs(actorCatalogFetchEvents);
  }

  public void workspaceServiceAccounts() throws JsonValidationException, IOException, ConfigNotFoundException {
    for (final WorkspaceServiceAccount expected : MockData.workspaceServiceAccounts()) {
      configPersistence.writeConfig(ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, expected.getWorkspaceId().toString(),
          expected);
      final WorkspaceServiceAccount actual = configPersistence.getConfig(
          ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, expected.getWorkspaceId().toString(), WorkspaceServiceAccount.class);
      assertEquals(expected, actual);
    }
    final List<WorkspaceServiceAccount> actorConfigurationBindings = configPersistence
        .listConfigs(ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, WorkspaceServiceAccount.class);
    assertEquals(MockData.workspaceServiceAccounts().size(), actorConfigurationBindings.size());
    assertThat(MockData.workspaceServiceAccounts()).hasSameElementsAs(actorConfigurationBindings);
  }

}

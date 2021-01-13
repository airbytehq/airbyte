/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class ArchiveHandlerTest {

  private ConfigRepository configRepository;

  private JsonNode dbConfig;
  private PostgreSQLContainer<?> container;
  private Database database;
  private ArchiveHandler archiveHandler;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    dbConfig = null;
    container = mock(PostgreSQLContainer.class);
    database = mock(Database.class);
    archiveHandler = new ArchiveHandler("test-version", configRepository, database);
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
    container.close();
  }

  private StandardWorkspace generateWorkspace() {
    final UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;

    return new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withCustomerId(UUID.randomUUID())
        .withEmail("test@airbyte.io")
        .withName("test workspace")
        .withSlug("default")
        .withInitialSetupComplete(false)
        .withOnboardingComplete(true);
  }

  @Test
  void testEmptyMigration() throws JsonValidationException, IOException {
    archiveHandler.importData(archiveHandler.exportData());

    verify(configRepository, never()).writeStandardWorkspace(any());
    verify(configRepository, never()).writeStandardSource(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());
    verify(configRepository, never()).writeSourceConnection(any());
    verify(configRepository, never()).writeDestinationConnection(any());
    verify(configRepository, never()).writeStandardSync(any());
    verify(configRepository, never()).writeStandardSchedule(any());
  }

  @Test
  void testConfigMigration() throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = generateWorkspace();
    final StandardSourceDefinition standardSource = SourceDefinitionHelpers.generateSource();
    final StandardDestinationDefinition standardDestination = DestinationDefinitionHelpers.generateDestination();
    final SourceConnection sourceConnection1 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final SourceConnection sourceConnection2 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final DestinationConnection destinationConnection = DestinationHelpers.generateDestination(standardDestination.getDestinationDefinitionId());
    final StandardSync destinationSync = ConnectionHelpers.generateSyncWithDestinationId(destinationConnection.getDestinationId());
    final StandardSync sourceSync = ConnectionHelpers.generateSyncWithSourceId(sourceConnection1.getSourceId());
    final StandardSyncSchedule syncSchedule = ConnectionHelpers.generateSchedule(sourceSync.getConnectionId());

    when(configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID))
        .thenReturn(workspace);
    when(configRepository.listStandardSources())
        .thenReturn(List.of(standardSource));
    when(configRepository.listStandardDestinationDefinitions())
        .thenReturn(List.of(standardDestination));
    when(configRepository.listSourceConnection())
        .thenReturn(List.of(sourceConnection1, sourceConnection2));
    when(configRepository.listDestinationConnection())
        .thenReturn(List.of(destinationConnection));
    when(configRepository.listStandardSyncs())
        .thenReturn(List.of(destinationSync, sourceSync));
    when(configRepository.getStandardSyncSchedule(sourceSync.getConnectionId()))
        .thenReturn(syncSchedule);

    archiveHandler.importData(archiveHandler.exportData());

    verify(configRepository, times(1)).writeStandardWorkspace(workspace);
    verify(configRepository, times(1)).writeStandardSource(standardSource);
    verify(configRepository, times(1)).writeStandardDestinationDefinition(standardDestination);
    verify(configRepository, times(1)).writeSourceConnection(sourceConnection1);
    verify(configRepository, times(1)).writeSourceConnection(sourceConnection2);
    verify(configRepository, times(1)).writeDestinationConnection(destinationConnection);
    verify(configRepository, times(1)).writeStandardSync(sourceSync);
    verify(configRepository, times(1)).writeStandardSync(destinationSync);
    verify(configRepository, times(1)).writeStandardSchedule(syncSchedule);
  }

  @Test
  void testDatabaseMigration() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();
    dbConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()))
        .build());
    database = Databases.createPostgresDatabase(
        dbConfig.get("username").asText(),
        dbConfig.get("password").asText(),
        dbConfig.get("jdbc_url").asText());
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), updated_at DATE);");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, updated_at) VALUES (1,'picard', '2004-10-19'),  (2, 'crusher', '2005-10-19'), (3, 'vash', '2006-10-19');");
      return null;
    });
    archiveHandler = new ArchiveHandler("test-version", configRepository, database);

    archiveHandler.importData(archiveHandler.exportData());
  }

}

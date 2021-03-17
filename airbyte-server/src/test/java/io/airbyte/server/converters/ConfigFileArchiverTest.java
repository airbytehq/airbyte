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

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.ConfigSchema;
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
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class ConfigFileArchiverTest {

  private ConfigRepository configRepository;
  private ConfigFileArchiver configFileArchiver;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    configFileArchiver = new ConfigFileArchiver(configRepository);
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
        .withTombstone(false);
  }

  @Test
  void testConfigExportImport() throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = generateWorkspace();
    final StandardSourceDefinition standardSource = SourceDefinitionHelpers.generateSource();
    final StandardDestinationDefinition standardDestination = DestinationDefinitionHelpers.generateDestination();
    final SourceConnection sourceConnection1 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final SourceConnection sourceConnection2 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final DestinationConnection destinationConnection = DestinationHelpers.generateDestination(standardDestination.getDestinationDefinitionId());
    final StandardSync destinationSync = ConnectionHelpers.generateSyncWithDestinationId(destinationConnection.getDestinationId());
    final StandardSync sourceSync = ConnectionHelpers.generateSyncWithSourceId(sourceConnection1.getSourceId());
    final StandardSyncSchedule syncSchedule = ConnectionHelpers.generateSchedule(sourceSync.getConnectionId());

    // Read operations
    when(configRepository.listStandardWorkspaces(true)).thenReturn(List.of(workspace));
    when(configRepository.listStandardSources()).thenReturn(List.of(standardSource));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(standardDestination));
    when(configRepository.listSourceConnection()).thenReturn(List.of(sourceConnection1, sourceConnection2));
    when(configRepository.listDestinationConnection()).thenReturn(List.of(destinationConnection));
    when(configRepository.listStandardSyncs()).thenReturn(List.of(destinationSync, sourceSync));
    when(configRepository.getStandardSyncSchedule(sourceSync.getConnectionId())).thenReturn(syncSchedule);

    final Path tempFolder = Files.createTempDirectory("testConfigMigration");
    configFileArchiver.exportConfigsToArchive(tempFolder);
    configFileArchiver.importConfigsFromArchive(tempFolder, false);

    verify(configRepository).writeStandardWorkspace(workspace);
    verify(configRepository).writeStandardSource(standardSource);
    verify(configRepository).writeStandardDestinationDefinition(standardDestination);
    verify(configRepository).writeSourceConnection(sourceConnection1);
    verify(configRepository).writeSourceConnection(sourceConnection2);
    verify(configRepository).writeDestinationConnection(destinationConnection);
    verify(configRepository).writeStandardSync(sourceSync);
    verify(configRepository).writeStandardSync(destinationSync);
    verify(configRepository).writeStandardSchedule(syncSchedule);
  }

  @Test
  void testPartialConfigImport() throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = generateWorkspace();
    final StandardSourceDefinition standardSource = SourceDefinitionHelpers.generateSource();
    final StandardDestinationDefinition standardDestination = DestinationDefinitionHelpers.generateDestination();
    final SourceConnection sourceConnection1 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final SourceConnection sourceConnection2 = SourceHelpers.generateSource(standardSource.getSourceDefinitionId());
    final DestinationConnection destinationConnection = DestinationHelpers.generateDestination(standardDestination.getDestinationDefinitionId());
    final StandardSync destinationSync = ConnectionHelpers.generateSyncWithDestinationId(destinationConnection.getDestinationId());
    final StandardSync sourceSync = ConnectionHelpers.generateSyncWithSourceId(sourceConnection1.getSourceId());
    final StandardSyncSchedule syncSchedule = ConnectionHelpers.generateSchedule(sourceSync.getConnectionId());

    // Read operations
    when(configRepository.listStandardWorkspaces(true)).thenReturn(List.of(workspace));
    when(configRepository.listStandardSources()).thenReturn(List.of(standardSource));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(standardDestination));
    when(configRepository.listSourceConnection()).thenReturn(List.of(sourceConnection1, sourceConnection2));
    when(configRepository.listDestinationConnection()).thenReturn(List.of(destinationConnection));
    when(configRepository.listStandardSyncs()).thenReturn(List.of(destinationSync, sourceSync));
    when(configRepository.getStandardSyncSchedule(sourceSync.getConnectionId())).thenReturn(syncSchedule);

    final Path tempFolder = Files.createTempDirectory("testConfigMigration");
    configFileArchiver.exportConfigsToArchive(tempFolder);
    Files.delete(ConfigFileArchiver.buildConfigPath(tempFolder, ConfigSchema.STANDARD_DESTINATION_DEFINITION));
    assertThrows(RuntimeException.class, () -> configFileArchiver.importConfigsFromArchive(tempFolder, false));
  }

}

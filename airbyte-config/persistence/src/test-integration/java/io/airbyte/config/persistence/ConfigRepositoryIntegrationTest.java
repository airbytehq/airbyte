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

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigRepositoryIntegrationTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID2 = UUID.randomUUID();
  private static final UUID SOURCE_CONNECTION_ID = UUID.randomUUID();
  private static final UUID SOURCE_CONNECTION_ID2 = UUID.randomUUID();
  private static final UUID DEST_DEFINITION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_CONNECTION_ID = UUID.randomUUID();

  private ConfigPersistence configPersistence;
  private ConfigPersistence secretsConfigPersistence;
  private ConfigRepository configRepository;

  public static final UUID UUID_1 = new UUID(0, 1);
  public static final StandardSourceDefinition SOURCE_DEFINITION_1 = new StandardSourceDefinition();

  static {
    SOURCE_DEFINITION_1.withSourceDefinitionId(UUID_1).withName("mysql");
  }
  private static final SourceConnection SOURCE_CONNECTION = new SourceConnection()
        .withSourceId(SOURCE_CONNECTION_ID)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(Jsons.deserialize("{\"somefield\":\"secretvalue\"}"))
        .withName("source")
        .withTombstone(false);

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSourceDefinition SOURCE_DEFINITION_2 = new StandardSourceDefinition();
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  static {
    SOURCE_DEFINITION_2.withSourceDefinitionId(UUID_2).withName("mssql");
  }
  private static final SourceConnection SOURCE_CONNECTION_2 = new SourceConnection()
      .withSourceId(SOURCE_CONNECTION_ID2)
      .withSourceDefinitionId(SOURCE_DEFINITION_ID2)
      .withWorkspaceId(WORKSPACE_ID)
      .withConfiguration(Jsons.deserialize("{\"somefield\":\"secretvalue\"}"))
      .withName("source")
      .withTombstone(false);

  public static final UUID UUID_3 = new UUID(0, 3);
  public static final StandardDestinationDefinition DEST_3 = new StandardDestinationDefinition();
  static {
    DEST_3.withDestinationDefinitionId(UUID_3).withName("postgresql");
  }
  private static final DestinationConnection DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(DESTINATION_CONNECTION_ID)
      .withDestinationDefinitionId(DEST_DEFINITION_ID)
      .withWorkspaceId(WORKSPACE_ID)
      .withConfiguration(Jsons.deserialize("{\"somefield\":\"secretvalue\"}"))
      .withName("dest")
      .withTombstone(false);


  @BeforeEach
  void setup() throws IOException {
    Path p = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), this.getClass().getName());
    Files.createDirectories(new File(p.toAbsolutePath() + "/config").toPath());

    configPersistence = new FileSystemConfigPersistence(p);
    secretsConfigPersistence = new GoogleSecretsManagerConfigPersistence(WORKSPACE_ID);
    configRepository = new ConfigRepository(configPersistence, secretsConfigPersistence);
  }

  @AfterEach
  void tearDown() throws IOException {
    // Delete all the secrets we stored for testing in this temporary workspace.
    String prefix = ((GoogleSecretsManagerConfigPersistence) secretsConfigPersistence).getVersion() + "-"
        + ((GoogleSecretsManagerConfigPersistence) secretsConfigPersistence).getWorkspacePattern();
    List<String> names = GoogleSecretsManager.listSecretsMatching(prefix);
    for (String name : names) {
      GoogleSecretsManager.deleteSecret(name);
    }
  }

  // Make sure we can add configs and then replace them with updated ones, and the updates take.
  @Test
  void replaceAllConfigsSeeUpdates() throws IOException {
    Map<AirbyteConfig, Stream<Object>> map =  new LinkedHashMap<>();
    map.put(ConfigSchema.SOURCE_CONNECTION, Stream.of(SOURCE_CONNECTION, SOURCE_CONNECTION_2));
    map.put(ConfigSchema.DESTINATION_CONNECTION, Stream.of(DESTINATION_CONNECTION));
    configRepository.replaceAllConfigs(map, true);

    map.put(ConfigSchema.SOURCE_CONNECTION, Stream.of(SOURCE_CONNECTION, SOURCE_CONNECTION_2));
    map.put(ConfigSchema.DESTINATION_CONNECTION, Stream.of(DESTINATION_CONNECTION));
    configRepository.replaceAllConfigs(map,false);

    // TODO: Reload them and check to see that all the expected contents are there?
  }

  @Test
  void replaceAllConfigsEmptySet() throws IOException {
    // Make sure we can call replaceAll on an empty set and it doesn't crash.
    Map<AirbyteConfig, Stream<Object>> map =  new LinkedHashMap<>();
    configRepository.replaceAllConfigs(map, true);
    configRepository.replaceAllConfigs(map,false);
  }

  @Test
  void replaceAllConfigsSecretsLocation() throws IOException {
    // Make sure that secrets are written out to the correct secret store and don't show up in the wrong one.

    Map<AirbyteConfig, Stream<Object>> map =  new LinkedHashMap<>();
    map.put(ConfigSchema.SOURCE_CONNECTION, Stream.of(SOURCE_CONNECTION, SOURCE_CONNECTION_2));
    map.put(ConfigSchema.DESTINATION_CONNECTION, Stream.of(DESTINATION_CONNECTION));
    configRepository.replaceAllConfigs(map, false);

    Map<String, Stream<JsonNode>> nonsecret = configPersistence.dumpConfigs();
    assert(nonsecret.size() == 0);

    Map<String, Stream<JsonNode>> secret = secretsConfigPersistence.dumpConfigs();
    assert(secret.size() == 2);
  }

  @Test
  void dumpConfigs() throws IOException {
    // 1. Make sure we can store some configs and then do a dump and they're all included.
    // 2. Make sure we can see both of configs from a non-secret store and configs from a secret store.
    Map<AirbyteConfig, Stream<Object>> map =  new LinkedHashMap<>();

    // These should land in the secrets store, so they're the core of testing.
    map.put(ConfigSchema.SOURCE_CONNECTION, Stream.of(SOURCE_CONNECTION, SOURCE_CONNECTION_2));
    map.put(ConfigSchema.DESTINATION_CONNECTION, Stream.of(DESTINATION_CONNECTION));

    // We're checking serialization for all the rest of these, to make sure nothing explodes during storage and they are retained.
    map.put(ConfigSchema.STANDARD_WORKSPACE, Stream.of(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withCustomerId(UUID.randomUUID())));
    map.put(ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID())));
    map.put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, Stream.of(new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID())));
    map.put(ConfigSchema.STANDARD_SYNC, Stream.of(new StandardSync()
        .withName("sync")
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("sync")
        .withConnectionId(SOURCE_CONNECTION_ID)
        .withSourceId(UUID.randomUUID())
        .withDestinationId(UUID.randomUUID())
        .withOperationIds(List.of(UUID.randomUUID()))));
    map.put(ConfigSchema.STANDARD_SYNC_OPERATION, Stream.of(new StandardSyncOperation().withOperationId(UUID.randomUUID())));

    // Now retrieve what we stored and make sure we got everything.
    configRepository.replaceAllConfigs(map, false);

    Map<String, Stream<JsonNode>> configs = configRepository.dumpConfigs();
    assertNotNull(configs.get(ConfigSchema.SOURCE_CONNECTION.name()));
    assertNotNull(configs.get(ConfigSchema.DESTINATION_CONNECTION.name()));
    assertNotNull(configs.get(ConfigSchema.STANDARD_WORKSPACE.name()));
    assertNotNull(configs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()));
    assertNotNull(configs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()));
    assertNotNull(configs.get(ConfigSchema.STANDARD_SYNC.name()));
    assertNotNull(configs.get(ConfigSchema.STANDARD_SYNC_OPERATION.name()));
  }

}

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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import com.google.common.collect.Sets;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardSource;
import io.airbyte.config.StandardSync;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultConfigPersistenceTest {

  public static final UUID UUID_1 = new UUID(0, 1);
  public static final StandardSource SOURCE_1 = new StandardSource();

  static {
    SOURCE_1.withSourceId(UUID_1)
        .withName("apache storm");
  }

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSource SOURCE_2 = new StandardSource();
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  static {
    SOURCE_2.withSourceId(UUID_2)
        .withName("apache storm");
  }

  private Path rootPath;
  private JsonSchemaValidator schemaValidator;

  private DefaultConfigPersistence configPersistence;

  @BeforeEach
  void setUp() throws IOException {
    schemaValidator = mock(JsonSchemaValidator.class);
    rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), DefaultConfigPersistenceTest.class.getName());

    configPersistence = new DefaultConfigPersistence(rootPath, schemaValidator);
  }

  @Test
  void testReadWriteConfig() throws IOException, JsonValidationException, ConfigNotFoundException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE, UUID_1.toString(), SOURCE_1);

    assertEquals(
        SOURCE_1,
        configPersistence.getConfig(
            ConfigSchema.STANDARD_SOURCE,
            UUID_1.toString(),
            StandardSource.class));
  }

  @Test
  void testListConfigs() throws JsonValidationException, IOException, ConfigNotFoundException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE, UUID_1.toString(), SOURCE_1);
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE, UUID_2.toString(), SOURCE_2);

    assertEquals(
        Sets.newHashSet(SOURCE_1, SOURCE_2),
        Sets.newHashSet(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE, StandardSource.class)));
  }

  @Test
  void writeConfigWithJsonSchemaRef() throws JsonValidationException, IOException, ConfigNotFoundException {
    final Schema schema = new Schema();

    final StandardSync standardSync = new StandardSync()
        .withName("sync")
        .withConnectionId(UUID_1)
        .withSourceImplementationId(UUID.randomUUID())
        .withDestinationImplementationId(UUID.randomUUID())
        .withSyncMode(StandardSync.SyncMode.FULL_REFRESH)
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(schema);

    configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID_1.toString(), standardSync);

    assertEquals(
        standardSync,
        configPersistence.getConfig(ConfigSchema.STANDARD_SYNC, UUID_1.toString(), StandardSync.class));
  }

  @Test
  void writeConfigInvalidConfig() throws JsonValidationException {
    StandardSource standardSource = SOURCE_1.withName(null);

    doThrow(new JsonValidationException("error")).when(schemaValidator).ensure(any(), any());

    assertThrows(JsonValidationException.class, () -> configPersistence.writeConfig(
        ConfigSchema.STANDARD_SOURCE,
        UUID_1.toString(),
        standardSource));
  }

}

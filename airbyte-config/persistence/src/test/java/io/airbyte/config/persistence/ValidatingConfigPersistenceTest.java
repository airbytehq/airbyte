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
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ValidatingConfigPersistenceTest {

  public static final UUID UUID_1 = new UUID(0, 1);
  public static final StandardSourceDefinition SOURCE_1 = new StandardSourceDefinition();

  static {
    SOURCE_1.withSourceDefinitionId(UUID_1).withName("apache storm");
  }

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSourceDefinition SOURCE_2 = new StandardSourceDefinition();
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  static {
    SOURCE_2.withSourceDefinitionId(UUID_2).withName("apache storm");
  }

  private JsonSchemaValidator schemaValidator;

  private ValidatingConfigPersistence configPersistence;
  private ConfigPersistence decoratedConfigPersistence;

  @BeforeEach
  void setUp() {
    schemaValidator = mock(JsonSchemaValidator.class);

    decoratedConfigPersistence = mock(ConfigPersistence.class);
    configPersistence = new ValidatingConfigPersistence(decoratedConfigPersistence, schemaValidator);
  }

  @Test
  void testWriteConfigSuccess() throws IOException, JsonValidationException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
    verify(decoratedConfigPersistence).writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
  }

  @Test
  void testWriteConfigFailure() throws JsonValidationException {
    doThrow(new JsonValidationException("error")).when(schemaValidator).ensure(any(), any());
    assertThrows(JsonValidationException.class,
        () -> configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1));

    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testGetConfigSuccess() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(decoratedConfigPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(SOURCE_1);
    final StandardSourceDefinition actualConfig = configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class);

    assertEquals(SOURCE_1, actualConfig);
  }

  @Test
  void testGetConfigFailure() throws IOException, JsonValidationException, ConfigNotFoundException {
    doThrow(new JsonValidationException("error")).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(SOURCE_1);

    assertThrows(
        JsonValidationException.class,
        () -> configPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class));
  }

  @Test
  void testListConfigsSuccess() throws JsonValidationException, IOException {
    when(decoratedConfigPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(SOURCE_1, SOURCE_2));

    final List<StandardSourceDefinition> actualConfigs = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);

    assertEquals(
        Sets.newHashSet(SOURCE_1, SOURCE_2),
        Sets.newHashSet(actualConfigs));
  }

  @Test
  void testListConfigsFailure() throws JsonValidationException, IOException {
    doThrow(new JsonValidationException("error")).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(SOURCE_1, SOURCE_2));

    assertThrows(JsonValidationException.class, () -> configPersistence
        .listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class));
  }

}

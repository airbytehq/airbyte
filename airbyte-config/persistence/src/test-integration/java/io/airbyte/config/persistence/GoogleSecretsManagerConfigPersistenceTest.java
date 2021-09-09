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

import com.google.common.collect.Sets;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class GoogleSecretsManagerConfigPersistenceTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private GoogleSecretsManagerConfigPersistence configPersistence;

  public static final UUID UUID_1 = new UUID(0, 1);
  public static final StandardSourceDefinition SOURCE_1 = new StandardSourceDefinition();
  static {
    SOURCE_1.withSourceDefinitionId(UUID_1).withName("postgresql");
  }

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSourceDefinition SOURCE_2 = new StandardSourceDefinition();
  static {
    SOURCE_2.withSourceDefinitionId(UUID_2).withName("apache storm");
  }

  @BeforeEach
  void setUp() throws IOException {
    configPersistence = new GoogleSecretsManagerConfigPersistence();
  }

  @Test
  void testReadWriteConfig() throws IOException, JsonValidationException, ConfigNotFoundException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
    Assertions.assertEquals(SOURCE_1,
        configPersistence.getConfig(
            ConfigSchema.STANDARD_SOURCE_DEFINITION,
            UUID_1.toString(),
            StandardSourceDefinition.class));
  }

  @Test
  void testListConfigs() throws JsonValidationException, IOException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_2.toString(), SOURCE_2);

    Assertions.assertEquals(
        Sets.newHashSet(SOURCE_1, SOURCE_2),
        Sets.newHashSet(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)));
  }

  private void assertRecordCount(int expectedCount) throws Exception {
    // Result<Record1<Integer>> recordCount = database.query(ctx ->
    // ctx.select(count(asterisk())).from(table("airbyte_configs")).fetch());
    assertEquals(expectedCount, 999);// TODO: Fix // recordCount.get(0).value1());
  }

  private void assertHasSource(StandardSourceDefinition source) throws Exception {
    Assertions.assertEquals(source, configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(),
            StandardSourceDefinition.class));
  }

  private void assertHasDestination(StandardDestinationDefinition destination) throws Exception {
    Assertions.assertEquals(destination, configPersistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(),
            StandardDestinationDefinition.class));
  }

}

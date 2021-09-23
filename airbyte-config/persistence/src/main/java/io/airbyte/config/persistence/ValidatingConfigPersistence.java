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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

// we force all interaction with disk storage to be effectively single threaded.
public class ValidatingConfigPersistence implements ConfigPersistence {

  private final JsonSchemaValidator schemaValidator;
  private final ConfigPersistence decoratedPersistence;

  public ValidatingConfigPersistence(final ConfigPersistence decoratedPersistence) {
    this(decoratedPersistence, new JsonSchemaValidator());
  }

  public ValidatingConfigPersistence(final ConfigPersistence decoratedPersistence, final JsonSchemaValidator schemaValidator) {
    this.decoratedPersistence = decoratedPersistence;
    this.schemaValidator = schemaValidator;
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final T config = decoratedPersistence.getConfig(configType, configId, clazz);
    validateJson(config, configType);
    return config;
  }

  @Override
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException {
    final List<T> configs = decoratedPersistence.listConfigs(configType, clazz);
    for (T config : configs) {
      validateJson(config, configType);
    }
    return configs;
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException {
    validateJson(Jsons.jsonNode(config), configType);
    decoratedPersistence.writeConfig(configType, configId, config);
  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException {
    decoratedPersistence.deleteConfig(configType, configId);
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    // todo (cgardens) need to do validation here.
    decoratedPersistence.replaceAllConfigs(configs, dryRun);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    return decoratedPersistence.dumpConfigs();
  }

  @Override
  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    decoratedPersistence.loadData(seedPersistence);
  }

  private <T> void validateJson(T config, AirbyteConfig configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getConfigSchemaFile());
    schemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

}

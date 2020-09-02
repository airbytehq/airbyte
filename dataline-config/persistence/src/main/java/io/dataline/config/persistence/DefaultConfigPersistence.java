/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.dataline.commons.json.Jsons;
import io.dataline.config.ConfigSchema;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import me.andrz.jackson.JsonReferenceException;
import me.andrz.jackson.JsonReferenceProcessor;

// we force all interaction with disk storage to be effectively single threaded.
public class DefaultConfigPersistence implements ConfigPersistence {

  private static final Object lock = new Object();

  private final JsonSchemaValidator jsonSchemaValidator;
  private final Path storageRoot;

  public DefaultConfigPersistence(final Path storageRoot) {
    this(storageRoot, new JsonSchemaValidator());
  }

  public DefaultConfigPersistence(final Path storageRoot, final JsonSchemaValidator schemaValidator) {
    this.storageRoot = storageRoot;
    jsonSchemaValidator = schemaValidator;
  }

  @Override
  public <T> T getConfig(final ConfigSchema persistenceConfigType,
                         final String configId,
                         final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    synchronized (lock) {
      return getConfigInternal(persistenceConfigType, configId, clazz);
    }
  }

  @Override
  public <T> List<T> listConfigs(ConfigSchema persistenceConfigType,
                                 Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    synchronized (lock) {
      return listConfigsInternal(persistenceConfigType, clazz);
    }
  }

  @Override
  public <T> void writeConfig(ConfigSchema persistenceConfigType,
                              String configId,
                              T config)
      throws JsonValidationException, IOException {
    synchronized (lock) {
      writeConfigInternal(persistenceConfigType, configId, config);
    }
  }

  private <T> T getConfigInternal(ConfigSchema configType,
                                  String configId,
                                  Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    // validate file with schema
    final Path configPath = buildConfigPath(configType, configId);
    if (!Files.exists(configPath)) {
      throw new ConfigNotFoundException(configType, configId);
    }

    final T config = Jsons.deserialize(Files.readString(configPath), clazz);
    validateJson(config, configType);

    return config;
  }

  private <T> List<T> listConfigsInternal(ConfigSchema persistenceConfigType,
                                          Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Path configTypePath = buildTypePath(persistenceConfigType);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }

    List<String> ids = Files.list(configTypePath)
        .filter(p -> !p.endsWith(".json"))
        .map(p -> p.getFileName().toString().replace(".json", ""))
        .collect(Collectors.toList());

    final List<T> configs = Lists.newArrayList();
    for (String id : ids) {
      configs.add(getConfig(persistenceConfigType, id, clazz));
    }

    return configs;
  }

  private <T> void writeConfigInternal(ConfigSchema persistenceConfigType,
                                       String configId,
                                       T config)
      throws JsonValidationException, IOException {
    // validate config with schema
    validateJson(Jsons.jsonNode(config), persistenceConfigType);

    final Path configPath = buildConfigPath(persistenceConfigType, configId);
    Files.createDirectories(configPath.getParent());

    Files.writeString(configPath, Jsons.serialize(config));
  }

  private Path buildConfigPath(ConfigSchema type, String configId) {
    return buildTypePath(type).resolve(String.format("%s.json", configId));
  }

  private Path buildTypePath(ConfigSchema type) {
    return storageRoot.resolve(type.toString());
  }

  private <T> void validateJson(T config, ConfigSchema persistenceConfigType) throws JsonValidationException {
    JsonNode schema = getSchema(persistenceConfigType);
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

  @VisibleForTesting
  private JsonNode getSchema(ConfigSchema configType) {
    try {
      // JsonReferenceProcessor follows $ref in json objects. Jackson does not natively support
      // this.
      final JsonReferenceProcessor jsonReferenceProcessor = new JsonReferenceProcessor();
      jsonReferenceProcessor.setMaxDepth(-1); // no max.
      return jsonReferenceProcessor.process(configType.getFile());
    } catch (IOException | JsonReferenceException e) {
      throw new RuntimeException(e);
    }
  }

}

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
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;

public class GoogleSecretsManagerConfigPersistence implements ConfigPersistence {

  protected UUID workspaceId;

  public GoogleSecretsManagerConfigPersistence(UUID workspaceId) {
    this.workspaceId = workspaceId;
  }

  /**
   * Determines the secrets manager key name for storing a particular config
   */
  protected <T> String generateKeyNameFromType(AirbyteConfig configType, String configId) {
    return String.format("secrets-v1-workspace-%s-%s-%s-configuration", this.workspaceId, configType.getIdFieldName(), configId);
  }
  protected <T> String generateKeyPrefixFromType(AirbyteConfig configType) {
    return String.format("secrets-v1-workspace-%s-%s-", this.workspaceId, configType.getIdFieldName());
  }

  @Override
  public <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    return Jsons.deserialize(GoogleSecretsManager.readSecret(keyName), clazz);
  }

  @Override
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException {
    List<T> configs = new ArrayList<T>();
    for (String keyName : GoogleSecretsManager.listSecretsMatching(generateKeyPrefixFromType(configType))) {
      configs.add(Jsons.deserialize(GoogleSecretsManager.readSecret(keyName), clazz));
    }
    return configs;
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    String configuration = Jsons.serialize(config);
    GoogleSecretsManager.saveSecret(keyName, configuration);
  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    GoogleSecretsManager.deleteSecret(keyName);
  }

  @Override
  public <T> void replaceAllConfigs(Map<AirbyteConfig, Stream<T>> configs, boolean dryRun) throws IOException {
    // TODO Implement
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    // TODO Implement
    return null;
  }

}

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

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Provides an easy way of accessing a set of resource files in a specific directory when testing
 * secrets-related helpers.
 */
public interface SecretsTestCase {

  String getName();

  Map<SecretCoordinate, String> getFirstSecretMap();

  Map<SecretCoordinate, String> getSecondSecretMap();

  Consumer<SecretPersistence> getPersistenceUpdater();

  default ConnectorSpecification getSpec() {
    return Exceptions.toRuntime(() -> new ConnectorSpecification().withConnectionSpecification(getNodeResource(getName(), "spec.json")));
  }

  default JsonNode getFullConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "full_config.json"));
  }

  default JsonNode getPartialConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "partial_config.json"));
  }

  default JsonNode getUpdateConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "update_config.json"));
  }

  default JsonNode getUpdatedPartialConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "updated_partial_config.json"));
  }

  default JsonNode getNodeResource(String testCase, String fileName) throws IOException {
    return Jsons.deserialize(MoreResources.readResource(testCase + "/" + fileName));
  }

}

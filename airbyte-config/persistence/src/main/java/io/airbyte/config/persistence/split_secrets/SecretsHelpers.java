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

import com.fasterxml.jackson.core.JsonPointer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.Preconditions;
import com.jayway.jsonpath.JsonPath;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

public class SecretsHelpers {

  // todo: double check oauth stuff that's already in place
  // todo: create an in memory singleton map secrets store implementation for testing
  // todo: create a separate persistence for secrets that doesn't have config types, is just string to
  // string and allows configuration for a specific prefix
  // todo: test behavior for optional secrets (like the switching in files for example)
  // todo: test an array of secrets - what if you have an array of oneOf? - harddest case is an array
  // of oneofs?
  // todo: CREATION spec + full config -> coordconfig+secrets

    public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {
        return split(uuidSupplier, workspaceId, fullConfig, spec.getConnectionSpecification());
    }

  private static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, JsonNode spec) {

      // todo: check if these are necessary
      final var obj = fullConfig.deepCopy();
      final var schema = spec.deepCopy();
      final var secretMap = new HashMap<String, String>();

      System.out.println("schema = " + schema);
      Preconditions.checkArgument(JsonSecretsProcessor.canBeProcessed(schema), "Schema is not valid JSONSchema!");

      // get the properties field
      ObjectNode properties = (ObjectNode) schema.get(JsonSecretsProcessor.PROPERTIES_FIELD);
      JsonNode copy = obj.deepCopy();
      // for the property keys
      for (String key : Jsons.keys(properties)) {
          JsonNode fieldSchema = properties.get(key);
          // if the json schema field is an obj and has the airbyte secret field
          if (JsonSecretsProcessor.isSecret(fieldSchema) && copy.has(key)) {
              // remove the key put the new key in the coordinate section
              if (copy.has(key)) {
                  Preconditions.checkArgument(copy.get(key).isTextual(), "Secrets must be strings!");
                  final var secret = copy.get(key).asText();
                  final var secretUuid = uuidSupplier.get();
                  final var secretCoordinate = "workspace_" + workspaceId + "_secret_" + secretUuid + "_v1";
                  secretMap.put(secretCoordinate, secret);
                  ((ObjectNode) copy).replace(key, Jsons.jsonNode(Map.of("_secret", secretCoordinate)));
              }
          }

          var combinationKey = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);
          if (combinationKey.isPresent() && copy.has(key)) {
              var combinationCopy = copy.get(key);
              var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
              for (int i = 0; i < arrayNode.size(); i++) {
                  // Mask field values if any of the combination option is declaring it as secrets
                  final var combinationSplitConfig = split(uuidSupplier, workspaceId, combinationCopy, arrayNode.get(i));
                  combinationCopy = combinationSplitConfig.getPartialConfig();
                  secretMap.putAll(combinationSplitConfig.getSecretIdToPayload());
              }
              ((ObjectNode) copy).set(key, combinationCopy);
          } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("object") && fieldSchema.has("properties") && copy.has(key)) {
              final var nestedSplitConfig = split(uuidSupplier, workspaceId, copy.get(key), fieldSchema);
              ((ObjectNode) copy).replace(key, nestedSplitConfig.getPartialConfig());
              secretMap.putAll(nestedSplitConfig.getSecretIdToPayload());
          }
          // todo: also support just arrays here
      }

      return new SplitSecretConfig(copy, secretMap);
    // todo: come up with a better name than partialConfig
  }

  // todo: UPDATES old coordconfig+spec+ full config -> coordconfig+secrets
  public static SplitSecretConfig splitUpdate(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode oldPartialConfig, JsonNode newFullConfig, ConnectorSpecification spec) {
      // return null
  }

  // todo: READ coordconfig+secets persistence -> full config
  // todo: we'll want permissioning here at some point
  public static JsonNode combine(JsonNode partialConfig, ConfigPersistence secretsPersistence) {
    return null;
  }

  // todo: figure out oauth here
  // todo: test edge cases for json path definitino -> maybe can keep as a tree type or something
}

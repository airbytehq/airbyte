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
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.fasterxml.jackson.databind.node.ValueNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

public class SecretsHelpers {
  // todo: add airbyte_ prefix so our secrets are identifiable in the store
  // todo: double check oauth stuff that's already in place
  // todo: create an in memory singleton map secrets store implementation for testing
  // todo: create a separate persistence for secrets that doesn't have config types, is just string to
  // string and allows configuration for a specific prefix
  // todo: test behavior for optional secrets (like the switching in files for example)
  // todo: test an array of secrets - what if you have an array of oneOf? - harddest case is an array
  // of oneofs?
  // todo: CREATION spec + full config -> coordconfig+secrets

  public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, Jsons.emptyObject(), fullConfig, spec.getConnectionSpecification());
  }

  private static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode oldConfig, JsonNode fullConfig, JsonNode spec) {

    final var old = oldConfig.deepCopy();
    // todo: check if these are necessary
    final var obj = fullConfig.deepCopy();
    final var schema = spec.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();

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
        Preconditions.checkArgument(copy.get(key).isTextual(), "Secrets must be strings!");
        final var secret = copy.get(key).asText();
        UUID secretUuid;

        String coordinateBase = null;
        var version = 1L;
        if (old.has(key)) {
          final var oldSecret = old.get(key);

          if (oldSecret.has("_secret")) {
            var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecret.get("_secret").asText());
            coordinateBase = oldCoordinate.getCoordinateBase();
            version = oldCoordinate.getVersion() + 1;
          }
        }

        if (coordinateBase == null) {
          coordinateBase = "workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
        }

        final var secretCoordinate = new SecretCoordinate(coordinateBase, version);

        secretMap.put(secretCoordinate, secret);
        ((ObjectNode) copy).replace(key, Jsons.jsonNode(Map.of("_secret", secretCoordinate.toString())));
      }

      var combinationKey = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);
      if (combinationKey.isPresent() && copy.has(key)) {
        var combinationCopy = copy.get(key);
        var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
        for (int i = 0; i < arrayNode.size(); i++) {
          final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
          final var combinationSplitConfig = split(uuidSupplier, workspaceId, newOld, combinationCopy, arrayNode.get(i));
          combinationCopy = combinationSplitConfig.getPartialConfig();
          secretMap.putAll(combinationSplitConfig.getCoordinateToPayload());
        }
        ((ObjectNode) copy).set(key, combinationCopy);
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("object") && fieldSchema.has("properties") && copy.has(key)) {
        final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
        System.out.println("newOld 2 = " + newOld);
        final var nestedSplitConfig = split(uuidSupplier, workspaceId, newOld, copy.get(key), fieldSchema);
        ((ObjectNode) copy).replace(key, nestedSplitConfig.getPartialConfig());
        secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
      }
      // todo: also support just arrays here
    }

    return new SplitSecretConfig(copy, secretMap);
    // todo: come up with a better name than partialConfig
  }
  // todo: turn this into a generic iterator over all data so it's easier to manage across
  // JsonSecretsprocessor, here, and combine

  // todo: UPDATES old coordconfig+spec+ full config -> coordconfig+secrets
  public static SplitSecretConfig splitUpdate(Supplier<UUID> uuidSupplier,
                                              UUID workspaceId,
                                              JsonNode oldPartialConfig,
                                              JsonNode newFullConfig,
                                              ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, oldPartialConfig, newFullConfig, spec.getConnectionSpecification());
  }

  // todo: determine if versions should always upgrade or if it should check before incrementing to
  // see if it's the same value?

  // todo: READ coordconfig+secets persistence -> full config
  // todo: we'll want permissioning here at some point

  public static JsonNode combine(JsonNode partialConfig, SecretPersistence secretPersistence) {
    return combine(true, partialConfig, secretPersistence);
  }

  private static JsonNode combine(boolean isFirst, JsonNode partialConfig, SecretPersistence secretPersistence) {
    // todo: add wrapper that hides isFirst
    // todo: add test to make sure we aren't modifying input jsonnodes ever for any of the tests
    final var config = isFirst ? partialConfig.deepCopy() : partialConfig;

    System.out.println("========");

    config.fields().forEachRemaining(field -> {
      System.out.println("field.getKey() = " + field.getKey());

      final var node = field.getValue();
      final var childFields = MoreStreams.toStream(node.fields()).collect(Collectors.toList());
      for (Map.Entry<String, JsonNode> childField : childFields) {
        final var childNode = childField.getValue();
        System.out.println("childField.getKey() = " + childField.getKey());

        if (childField.getKey().equals("_secret")) {
          System.out.println("replacing parent");
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.asText());
          ((ObjectNode) config).replace(field.getKey(), new TextNode(secretPersistence.read(coordinate).get())); // todo: handle missing case
          break;
        } else if (childNode.has("_secret")) {
          System.out.println("replacing...");
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.get("_secret").asText());
          ((ObjectNode) node).replace(childField.getKey(), new TextNode(secretPersistence.read(coordinate).get())); // todo: handle missing case
        } else {
          System.out.println("not replacing");
        }
      }

      if (!(node instanceof ValueNode)) {
        combine(false, node, secretPersistence);
      } else {
        System.out.println("in else: " + node);
      }
    });
    return config;
  }

  // todo: figure out oauth here
  // todo: test edge cases for json path definitino -> maybe can keep as a tree type or something
}

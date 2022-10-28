/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class JsonDefinitionsHelper {

  public static JsonNode addMissingTombstoneField(final JsonNode definitionJson) {
    final JsonNode currTombstone = definitionJson.get("tombstone");
    if (currTombstone == null || currTombstone.isNull()) {
      ((ObjectNode) definitionJson).set("tombstone", BooleanNode.FALSE);
    }
    return definitionJson;
  }

  public static JsonNode addMissingPublicField(final JsonNode definitionJson) {
    final JsonNode currPublic = definitionJson.get("public");
    if (currPublic == null || currPublic.isNull()) {
      // definitions loaded from seed yamls are by definition public
      ((ObjectNode) definitionJson).set("public", BooleanNode.TRUE);
    }
    return definitionJson;
  }

  public static JsonNode addMissingCustomField(final JsonNode definitionJson) {
    final JsonNode currCustom = definitionJson.get("custom");
    if (currCustom == null || currCustom.isNull()) {
      // definitions loaded from seed yamls are by definition not custom
      ((ObjectNode) definitionJson).set("custom", BooleanNode.FALSE);
    }
    return definitionJson;
  }

}

/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteProtocolSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.function.Predicate;

public class AirbyteProtocolPredicate implements Predicate<JsonNode> {

  private final JsonSchemaValidator jsonSchemaValidator;
  private final JsonNode schema;

  public AirbyteProtocolPredicate() {
    jsonSchemaValidator = new JsonSchemaValidator();
    schema = JsonSchemaValidator.getSchema(AirbyteProtocolSchema.PROTOCOL.getFile(), "AirbyteMessage");
  }

  @Override
  public boolean test(JsonNode s) {
    return jsonSchemaValidator.test(schema, s);
  }

}

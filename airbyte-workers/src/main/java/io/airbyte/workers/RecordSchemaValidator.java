/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;

public class RecordSchemaValidator {

  public void validateSchema(final AirbyteMessage message, final StandardSyncInput syncInput) throws RecordSchemaValidationException {
    // the stream this message corresponds to
    final String messageStream = message.getRecord().getStream();
    final JsonNode messageData = message.getRecord().getData();
    final String streamPrefix = syncInput.getPrefix();

    // the stream name and json schema
    final ConfiguredAirbyteStream matchingAirbyteStream = syncInput.getCatalog().getStreams().stream()
        .filter(s -> (String.format(streamPrefix + s.getStream().getName().trim()).equals((messageStream.trim())))).findFirst().orElse(null);

    final JsonNode matchingSchema = matchingAirbyteStream.getStream().getJsonSchema();

    final JsonSchemaValidator validator = new JsonSchemaValidator();

    // We must choose a JSON validator version for validating the schema
    // Rather than allowing connectors to use any version, we enforce validation using V7
    ((ObjectNode) matchingSchema).put("$schema", "http://json-schema.org/draft-07/schema#");

    try {
      validator.ensure(matchingSchema, messageData);
    } catch (final JsonValidationException e) {
      throw new RecordSchemaValidationException(String.format("Record schema validation failed. Errors: %s", e.getMessage(), e));
    }
  }

}

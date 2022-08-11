/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.exception.RecordSchemaValidationException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Validates that AirbyteRecordMessage data conforms to the JSON schema defined by the source's
 * configured catalog
 */

public class RecordSchemaValidator {

  private final Map<String, JsonNode> streams;

  public RecordSchemaValidator(final Map<String, JsonNode> streamNamesToSchemas) {
    // streams is Map of a stream source namespace + name mapped to the stream schema
    // for easy access when we check each record's schema
    this.streams = streamNamesToSchemas;
  }

  /**
   * Takes an AirbyteRecordMessage and uses the JsonSchemaValidator to validate that its data conforms
   * to the stream's schema If it does not, this method throws a RecordSchemaValidationException
   *
   * @param message
   * @throws RecordSchemaValidationException
   */
  public void validateSchema(final AirbyteRecordMessage message, final String messageStream) throws RecordSchemaValidationException {
    final JsonNode messageData = message.getData();
    final JsonNode matchingSchema = streams.get(messageStream);

    final JsonSchemaValidator validator = new JsonSchemaValidator();

    // We must choose a JSON validator version for validating the schema
    // Rather than allowing connectors to use any version, we enforce validation using V7
    ((ObjectNode) matchingSchema).put("$schema", "http://json-schema.org/draft-07/schema#");

    try {
      validator.ensure(matchingSchema, messageData);
    } catch (final JsonValidationException e) {
      final List<String[]> invalidRecordDataAndType = validator.getValidationMessageArgs(matchingSchema, messageData);
      final List<String> invalidFields = validator.getValidationMessagePaths(matchingSchema, messageData);

      final Set<String> validationMessagesToDisplay = new HashSet<>();
      for (int i = 0; i < invalidFields.size(); i++) {
        final StringBuilder expectedType = new StringBuilder();
        if (invalidRecordDataAndType.size() > i && invalidRecordDataAndType.get(i).length > 1) {
          expectedType.append(invalidRecordDataAndType.get(i)[1]);
        }
        final StringBuilder newMessage = new StringBuilder();
        newMessage.append(invalidFields.get(i));
        newMessage.append(" is of an incorrect type.");
        if (expectedType.length() > 0) {
          newMessage.append(" Expected it to be " + expectedType);
        }
        validationMessagesToDisplay.add(newMessage.toString());
      }

      throw new RecordSchemaValidationException(validationMessagesToDisplay,
          String.format("Record schema validation failed for %s", messageStream), e);
    }
  }

}

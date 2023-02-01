/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.PerfBackgroundJsonValidation;
import io.airbyte.featureflag.Workspace;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.exception.RecordSchemaValidationException;
import java.lang.invoke.MethodHandles;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Validates that AirbyteRecordMessage data conforms to the JSON schema defined by the source's
 * configured catalog
 */
public class RecordSchemaValidator {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private final FeatureFlagClient featureFlagClient;
  private final UUID workspaceId;
  private static final JsonSchemaValidator validator = new JsonSchemaValidator();
  private final Map<AirbyteStreamNameNamespacePair, JsonNode> streams;

  public RecordSchemaValidator(final FeatureFlagClient featureFlagClient,
                               final UUID workspaceId,
                               final Map<AirbyteStreamNameNamespacePair, JsonNode> streamNamesToSchemas) {
    this.featureFlagClient = featureFlagClient;
    this.workspaceId = workspaceId;
    // streams is Map of a stream source namespace + name mapped to the stream schema
    // for easy access when we check each record's schema
    this.streams = streamNamesToSchemas;
    // initialize schema validator to avoid creating validators each time.
    for (final AirbyteStreamNameNamespacePair stream : streamNamesToSchemas.keySet()) {
      // We must choose a JSON validator version for validating the schema
      // Rather than allowing connectors to use any version, we enforce validation using V7
      final var schema = streams.get(stream);
      ((ObjectNode) schema).put("$schema", "http://json-schema.org/draft-07/schema#");
      validator.initializeSchemaValidator(stream.toString(), schema);
    }

  }

  /**
   * Takes an AirbyteRecordMessage and uses the JsonSchemaValidator to validate that its data conforms
   * to the stream's schema If it does not, this method throws a RecordSchemaValidationException
   *
   * @param message
   * @throws RecordSchemaValidationException
   */
  public void validateSchema(final AirbyteRecordMessage message, final AirbyteStreamNameNamespacePair messageStream)
      throws RecordSchemaValidationException {

    final JsonNode messageData = message.getData();
    final JsonNode matchingSchema = streams.get(messageStream);

    if (workspaceId != null) {
      if (featureFlagClient.enabled(PerfBackgroundJsonValidation.INSTANCE, new Workspace(workspaceId))) {
        log.debug("feature flag enabled for workspace {}", workspaceId);
      } else {
        log.debug("feature flag disabled for workspace {}", workspaceId);
      }
    } else {
      log.debug("workspace id is null");
    }

    try {
      validator.ensureInitializedSchema(messageStream.toString(), messageData);
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

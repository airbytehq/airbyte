/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.validation.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SchemaValidatorsConfig;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import io.airbyte.commons.string.Strings;
import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import me.andrz.jackson.JsonContext;
import me.andrz.jackson.JsonReferenceException;
import me.andrz.jackson.JsonReferenceProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonSchemaValidator {

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonSchemaValidator.class);

  private final SchemaValidatorsConfig schemaValidatorsConfig;
  private final JsonSchemaFactory jsonSchemaFactory;

  public JsonSchemaValidator() {
    this.schemaValidatorsConfig = new SchemaValidatorsConfig();
    this.jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
  }

  public Set<String> validate(final JsonNode schemaJson, final JsonNode objectJson) {
    return validateInternal(schemaJson, objectJson)
        .stream()
        .map(ValidationMessage::getMessage)
        .collect(Collectors.toSet());
  }

  public List<String[]> getValidationMessageArgs(final JsonNode schemaJson, final JsonNode objectJson) {
    return validateInternal(schemaJson, objectJson)
        .stream()
        .map(ValidationMessage::getArguments)
        .collect(Collectors.toList());
  }

  public List<String> getValidationMessagePaths(final JsonNode schemaJson, final JsonNode objectJson) {
    return validateInternal(schemaJson, objectJson)
        .stream()
        .map(ValidationMessage::getPath)
        .collect(Collectors.toList());
  }

  // keep this internal as it returns a type specific to the wrapped library.
  private Set<ValidationMessage> validateInternal(final JsonNode schemaJson, final JsonNode objectJson) {
    Preconditions.checkNotNull(schemaJson);
    Preconditions.checkNotNull(objectJson);

    return jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig)
        .validate(objectJson);
  }

  public boolean test(final JsonNode schemaJson, final JsonNode objectJson) {
    final Set<ValidationMessage> validationMessages = validateInternal(schemaJson, objectJson);

    if (!validationMessages.isEmpty()) {
      LOGGER.info("JSON schema validation failed. \nerrors: {}", Strings.join(validationMessages, ", "));
    }

    return validationMessages.isEmpty();
  }

  public void ensure(final JsonNode schemaJson, final JsonNode objectJson) throws JsonValidationException {
    final Set<ValidationMessage> validationMessages = validateInternal(schemaJson, objectJson);
    if (validationMessages.isEmpty()) {
      return;
    }

    throw new JsonValidationException(String.format(
        "json schema validation failed when comparing the data to the json schema. \nErrors: %s \nSchema: \n%s",
        Strings.join(validationMessages, ", "),
        schemaJson.toPrettyString()));
  }

  public void ensureAsRuntime(final JsonNode schemaJson, final JsonNode objectJson) {
    try {
      ensure(schemaJson, objectJson);
    } catch (final JsonValidationException e) {
      throw new RuntimeException(e);
    }
  }

  private static JsonReferenceProcessor getProcessor() {
    // JsonReferenceProcessor follows $ref in json objects. Jackson does not natively support
    // this.
    final JsonReferenceProcessor jsonReferenceProcessor = new JsonReferenceProcessor();
    jsonReferenceProcessor.setMaxDepth(-1); // no max.

    return jsonReferenceProcessor;
  }

  /**
   * Get JsonNode for an object defined as the main object in a JsonSchema file. Able to create the
   * JsonNode even if the the JsonSchema refers to objects in other files.
   *
   * @param schemaFile - the schema file
   * @return schema object processed from across all dependency files.
   */
  public static JsonNode getSchema(final File schemaFile) {
    try {
      return getProcessor().process(schemaFile);
    } catch (final IOException | JsonReferenceException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Get JsonNode for an object defined in the "definitions" section of a JsonSchema file. Able to
   * create the JsonNode even if the the JsonSchema refers to objects in other files.
   *
   * @param schemaFile - the schema file
   * @param definitionStructName - get the schema from a struct defined in the "definitions" section
   *        of a JsonSchema file (instead of the main object in that file).
   * @return schema object processed from across all dependency files.
   */
  public static JsonNode getSchema(final File schemaFile, final String definitionStructName) {
    try {
      final JsonContext jsonContext = new JsonContext(schemaFile);
      return getProcessor().process(jsonContext, jsonContext.getDocument().get("definitions").get(definitionStructName));
    } catch (final IOException | JsonReferenceException e) {
      throw new RuntimeException(e);
    }
  }

}

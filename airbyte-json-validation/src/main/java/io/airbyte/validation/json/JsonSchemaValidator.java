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
import java.util.Set;
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

  public Set<ValidationMessage> validate(JsonNode schemaJson, JsonNode objectJson) {
    Preconditions.checkNotNull(schemaJson);
    Preconditions.checkNotNull(objectJson);

    return jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig)
        .validate(objectJson);
  }

  public boolean test(JsonNode schemaJson, JsonNode objectJson) {
    Set<ValidationMessage> validationMessages = validate(schemaJson, objectJson);

    if (!validationMessages.isEmpty()) {
      LOGGER.info("JSON schema validation failed. \nerrors: {}", Strings.join(validationMessages, ", "));
    }

    return validationMessages.isEmpty();
  }

  public void ensure(JsonNode schemaJson, JsonNode objectJson) throws JsonValidationException {
    final Set<ValidationMessage> validationMessages = validate(schemaJson, objectJson);
    if (validationMessages.isEmpty()) {
      return;
    }

    throw new JsonValidationException(String.format(
        "json schema validation failed. \nerrors: %s \nschema: \n%s \nobject: \n%s",
        Strings.join(validationMessages, ", "),
        schemaJson.toPrettyString(),
        objectJson.toPrettyString()));
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
    } catch (IOException | JsonReferenceException e) {
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
  public static JsonNode getSchema(final File schemaFile, String definitionStructName) {
    try {
      final JsonContext jsonContext = new JsonContext(schemaFile);
      return getProcessor().process(jsonContext, jsonContext.getDocument().get("definitions").get(definitionStructName));
    } catch (IOException | JsonReferenceException e) {
      throw new RuntimeException(e);
    }
  }

}

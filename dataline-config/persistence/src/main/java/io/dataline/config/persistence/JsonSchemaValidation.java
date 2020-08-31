/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SchemaValidatorsConfig;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import java.util.Set;
import java.util.stream.Collectors;

public class JsonSchemaValidation {
  private final SchemaValidatorsConfig schemaValidatorsConfig;
  private final JsonSchemaFactory jsonSchemaFactory;

  public JsonSchemaValidation() {
    this.schemaValidatorsConfig = new SchemaValidatorsConfig();
    this.jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
  }

  public Set<ValidationMessage> validate(JsonNode schemaJson, JsonNode configJson) {
    JsonSchema schema = jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig);

    return schema.validate(configJson);
  }

  public void validateThrow(JsonNode schemaJson, JsonNode configJson)
      throws JsonValidationException {
    final Set<ValidationMessage> validationMessages = validate(schemaJson, configJson);
    if (validationMessages.size() > 0) {
      throw new JsonValidationException(
          String.format(
              "json schema validation failed. \nerrors: %s \nschema: \n%s \nobject: \n%s",
              validationMessages.stream()
                  .map(ValidationMessage::toString)
                  .collect(Collectors.joining(",")),
              schemaJson.toPrettyString(),
              configJson.toPrettyString()));
    }
  }
}

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

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigAgainstSpecValidator {

  private static final String MAPPING_ERROR_MSG_TEMPLATE = "Error in mapping for %s: %s;\n";
  private static final String TYPES_MISMATCH_ERROR_MSG_TEMPLATE =
      "Type for \"%s\" doesn't match the spec. Actual type is: \"%s\", but expected: \"%s\";\n";
  private static final String MISS_MANDATORY_ARGS_ERROR_MSG_TEMPLATE =
      "Not all mandatory ars were defined in request config. Missed are: \"%s\";";

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigAgainstSpecValidator.class);

  public void validate(JsonNode configToCheck,
                       JsonNode connectionSpecification,
                       String operationType)
      throws Exception {
    LOGGER.info("Verifying received config for " + operationType);
    LOGGER.debug("Actual specification: " + configToCheck);

    // Collect mandatory fields to check later if all of them are filled
    final List<String> mandatoryArgsListToCheck = new ArrayList<>();
    final StringBuilder verificationErrors = new StringBuilder();
    final JsonNode requiredArgs = connectionSpecification.get("required");

    if (requiredArgs != null && !requiredArgs.isEmpty()) {
      requiredArgs.forEach(jsonNode -> {
        mandatoryArgsListToCheck.add(jsonNode.textValue());
      });
    }

    final JsonNode origSpecProperties = connectionSpecification.get("properties");
    LOGGER.debug("Expected specification: " + origSpecProperties);

    if (origSpecProperties != null && !origSpecProperties.isEmpty()) {
      origSpecProperties.fields().forEachRemaining(el -> {
        final String key = el.getKey();
        final JsonNode jsonNodeToVerify = configToCheck.get(key);
        if (jsonNodeToVerify != null) {
          // if we get here then value at least exists in real request, but still need to check its type
          // remove key from mandatory ergs list as it exists in request
          mandatoryArgsListToCheck.remove(key);

          final JsonNodeType nodeTypeToVerify = jsonNodeToVerify.getNodeType();
          JsonNodeType originJsonNodeType = null;
          try {
            originJsonNodeType = mapStringObjectTypeToJsonNodeType(
                el.getValue().get("type").asText());
          } catch (Exception e) {
            LOGGER.error(e.getMessage());
            verificationErrors
                .append(String.format(MAPPING_ERROR_MSG_TEMPLATE, key, e.getMessage()));
          }
          if (originJsonNodeType != null && !originJsonNodeType.equals(nodeTypeToVerify)) {
            verificationErrors.append(String.format(
                TYPES_MISMATCH_ERROR_MSG_TEMPLATE, key, nodeTypeToVerify, originJsonNodeType));
          }
        }
      });
    }

    // if mandatoryArgsListToCheck is not empty - that means that some args were not set in request
    if (!mandatoryArgsListToCheck.isEmpty()) {
      throw new Exception(String.format(MISS_MANDATORY_ARGS_ERROR_MSG_TEMPLATE, mandatoryArgsListToCheck));
    }

    if (verificationErrors.length() != 0) {
      throw new Exception("Verification error(s) occurred: " + verificationErrors.toString());
    }
    LOGGER.debug("Verification completed");
  }

  private JsonNodeType mapStringObjectTypeToJsonNodeType(String typeNameFromSpecSchema)
      throws Exception {
    if (typeNameFromSpecSchema == null) {
      return JsonNodeType.NULL;
    }

    switch (typeNameFromSpecSchema.toLowerCase()) {
      case "string":
        return JsonNodeType.STRING;
      case "integer":
        return JsonNodeType.NUMBER;
      case "number":
        return JsonNodeType.NUMBER;
      case "boolean":
        return JsonNodeType.BOOLEAN;
      case "object":
        return JsonNodeType.OBJECT;
      case "array":
        return JsonNodeType.ARRAY;
      case "binary":
        return JsonNodeType.BINARY;
      case "missing":
        return JsonNodeType.MISSING;
      case "null":
        return JsonNodeType.NULL;
      case "pojo":
        return JsonNodeType.POJO;
      default:
        throw new Exception("Unsupported type:" + typeNameFromSpecSchema);
    }
  }

}

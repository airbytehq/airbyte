/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.constants.AirbyteSecretConstants;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.Set;

/**
 * Generates a set of property names from the provided connection spec properties object that are
 * marked as secret.
 */
public class SpecMaskPropertyGenerator {

  /**
   * Builds a set of property names from the provided connection spec properties object that are
   * marked as secret.
   *
   * @param properties The connection spec properties.
   * @return A set of property names that have been marked as secret.
   */
  public Set<String> getSecretFieldNames(final JsonNode properties) {
    final Set<String> secretPropertyNames = new HashSet<>();
    if (properties != null && properties.isObject()) {
      final Iterator<Entry<String, JsonNode>> fields = properties.fields();
      while (fields.hasNext()) {
        final Entry<String, JsonNode> field = fields.next();

        /*
         * If the current field is an object, check if it represents a secret. If it does, add it to the set
         * of property names. If not, recursively call this method again with the field value to see if it
         * contains any secrets.
         *
         * If the current field is an array, recursively call this method for each field within the value to
         * see if any of those contain any secrets.
         */
        if (field.getValue().isObject()) {
          if (field.getValue().has(AirbyteSecretConstants.AIRBYTE_SECRET_FIELD)) {
            if (field.getValue().get(AirbyteSecretConstants.AIRBYTE_SECRET_FIELD).asBoolean()) {
              secretPropertyNames.add(field.getKey());
            }
          } else {
            secretPropertyNames.addAll(getSecretFieldNames(field.getValue()));
          }
        } else if (field.getValue().isArray()) {
          for (int i = 0; i < field.getValue().size(); i++) {
            secretPropertyNames.addAll(getSecretFieldNames(field.getValue().get(i)));
          }
        }
      }
    }

    return secretPropertyNames;
  }

}

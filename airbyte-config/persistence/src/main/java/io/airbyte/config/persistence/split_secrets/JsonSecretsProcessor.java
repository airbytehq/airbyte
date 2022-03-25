package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

public interface JsonSecretsProcessor {

  static final String AIRBYTE_SECRET_FIELD = "airbyte_secret";
  static final String PROPERTIES_FIELD = "properties";
  static final String TYPE_FIELD = "type";
  static final String ARRAY_TYPE_FIELD = "array";
  static final String ITEMS_FIELD = "items";

  /**
   * Returns a copy of the input object wherein any fields annotated with "airbyte_secret" in the
   * input schema are masked.
   * <p>
   * This method masks secrets both at the top level of the configuration object and in nested
   * properties in a oneOf.
   *
   * @param schema Schema containing secret annotations
   * @param obj Object containing potentially secret fields
   */
  JsonNode maskSecrets(final JsonNode obj, final JsonNode schema);

  /**
   * Returns a copy of the destination object in which any secret fields (as denoted by the input
   * schema) found in the source object are added.
   * <p>
   * This method absorbs secrets both at the top level of the configuration object and in nested
   * properties in a oneOf.
   *
   * @param src The object potentially containing secrets
   * @param dst The object to absorb secrets into
   * @param schema
   * @return
   */
  JsonNode copySecrets(final JsonNode src, final JsonNode dst, final JsonNode schema);

  static boolean isSecret(final JsonNode obj) {
    return obj.isObject() && obj.has(AIRBYTE_SECRET_FIELD) && obj.get(AIRBYTE_SECRET_FIELD).asBoolean();
  }
}

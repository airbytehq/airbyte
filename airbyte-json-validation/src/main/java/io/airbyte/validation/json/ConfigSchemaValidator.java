/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.validation.json;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Set;

public interface ConfigSchemaValidator<T extends Enum<T>> {

  Set<String> validate(T configType, JsonNode objectJson);

  boolean test(T configType, JsonNode objectJson);

  void ensure(T configType, JsonNode objectJson) throws JsonValidationException;

  void ensureAsRuntime(T configType, JsonNode objectJson);

}

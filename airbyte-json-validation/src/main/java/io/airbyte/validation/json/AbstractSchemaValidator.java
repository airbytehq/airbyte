/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.validation.json;

import com.fasterxml.jackson.databind.JsonNode;
import java.nio.file.Path;
import java.util.Set;

public abstract class AbstractSchemaValidator<T extends Enum<T>> implements ConfigSchemaValidator<T> {

  private final JsonSchemaValidator jsonSchemaValidator;

  public AbstractSchemaValidator() {
    this(new JsonSchemaValidator());
  }

  public AbstractSchemaValidator(final JsonSchemaValidator jsonSchemaValidator) {
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public abstract Path getSchemaPath(T configType);

  private JsonNode getSchemaJson(final T configType) {
    return JsonSchemaValidator.getSchema(getSchemaPath(configType).toFile());
  }

  @Override
  public final Set<String> validate(final T configType, final JsonNode objectJson) {
    return jsonSchemaValidator.validate(getSchemaJson(configType), objectJson);
  }

  @Override
  public final boolean test(final T configType, final JsonNode objectJson) {
    return jsonSchemaValidator.test(getSchemaJson(configType), objectJson);
  }

  @Override
  public final void ensure(final T configType, final JsonNode objectJson) throws JsonValidationException {
    jsonSchemaValidator.ensure(getSchemaJson(configType), objectJson);
  }

  @Override
  public final void ensureAsRuntime(final T configType, final JsonNode objectJson) {
    jsonSchemaValidator.ensureAsRuntime(getSchemaJson(configType), objectJson);
  }

}

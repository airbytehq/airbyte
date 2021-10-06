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
import java.nio.file.Path;
import java.util.Set;

public abstract class AbstractSchemaValidator<T extends Enum<T>> implements ConfigSchemaValidator<T> {

  private final JsonSchemaValidator jsonSchemaValidator;

  public AbstractSchemaValidator() {
    this(new JsonSchemaValidator());
  }

  public AbstractSchemaValidator(JsonSchemaValidator jsonSchemaValidator) {
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public abstract Path getSchemaPath(T configType);

  private JsonNode getSchemaJson(T configType) {
    return JsonSchemaValidator.getSchema(getSchemaPath(configType).toFile());
  }

  @Override
  public final Set<String> validate(T configType, JsonNode objectJson) {
    return jsonSchemaValidator.validate(getSchemaJson(configType), objectJson);
  }

  @Override
  public final boolean test(T configType, JsonNode objectJson) {
    return jsonSchemaValidator.test(getSchemaJson(configType), objectJson);
  }

  @Override
  public final void ensure(T configType, JsonNode objectJson) throws JsonValidationException {
    jsonSchemaValidator.ensure(getSchemaJson(configType), objectJson);
  }

  @Override
  public final void ensureAsRuntime(T configType, JsonNode objectJson) {
    jsonSchemaValidator.ensureAsRuntime(getSchemaJson(configType), objectJson);
  }

}

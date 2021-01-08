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

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;

public class RecordConsumer implements CloseableConsumer<JsonNode> {

  private final CloseableConsumer<JsonNode> consumer;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JsonNode schema;

  public RecordConsumer(BufferedWriter fileWriter, JsonSchemaValidator jsonSchemaValidator, JsonNode schema) {
    this.consumer = Yamls.listWriter(fileWriter);
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.schema = schema;
  }

  @Override
  public void accept(JsonNode jsonNode) {
    try {
      jsonSchemaValidator.ensure(schema, jsonNode);
      consumer.accept(jsonNode);
    } catch (JsonValidationException e) {
      throw new IllegalArgumentException("Output record does not conform to declared output schema", e);
    }
  }

  @Override
  public void close() throws Exception {
    consumer.close();
  }

}

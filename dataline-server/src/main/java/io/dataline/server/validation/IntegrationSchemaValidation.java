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

package io.dataline.server.validation;

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonSchemaValidator;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.helpers.ConfigFetchers;
import java.util.UUID;

public class IntegrationSchemaValidation {

  private final ConfigPersistence configPersistence;

  private final JsonSchemaValidator jsonSchemaValidator;

  public IntegrationSchemaValidation(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;

    this.jsonSchemaValidator = new JsonSchemaValidator();
  }

  public void validateSourceConnectionConfiguration(UUID sourceConnectionSpecificationId, JsonNode configJson)
      throws JsonValidationException {
    final SourceConnectionSpecification sourceConnectionSpecification =
        ConfigFetchers.getSourceConnectionSpecification(
            configPersistence, sourceConnectionSpecificationId);

    final JsonNode schemaJson = sourceConnectionSpecification.getSpecification();

    jsonSchemaValidator.ensure(schemaJson, configJson);
  }

  public void validateDestinationConnectionConfiguration(UUID destinationConnectionSpecificationId, JsonNode configJson)
      throws JsonValidationException {
    final DestinationConnectionSpecification destinationConnectionSpecification =
        ConfigFetchers.getDestinationConnectionSpecification(
            configPersistence, destinationConnectionSpecificationId);

    final JsonNode schemaJson = destinationConnectionSpecification.getSpecification();

    jsonSchemaValidator.ensure(schemaJson, configJson);
  }

}

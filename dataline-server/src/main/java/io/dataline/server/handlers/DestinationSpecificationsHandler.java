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

package io.dataline.server.handlers;

import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationSpecificationRead;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;

public class DestinationSpecificationsHandler {
  private final ConfigPersistence configPersistence;

  public DestinationSpecificationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public DestinationSpecificationRead getDestinationSpecification(
      DestinationIdRequestBody destinationIdRequestBody) {
    final DestinationConnectionSpecification destinationConnection;
    try {
      // todo (cgardens) - this is a shortcoming of rolling our own disk storage. since we are not
      //   querying on a the primary key, we have to list all of the specification objects and then
      //   filter.
      destinationConnection =
          configPersistence
              .getConfigs(
                  PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
                  DestinationConnectionSpecification.class)
              .stream()
              .filter(
                  destinationSpecification ->
                      destinationSpecification
                          .getDestinationId()
                          .equals(destinationIdRequestBody.getDestinationId()))
              .findFirst()
              .orElseThrow(
                  () ->
                      new KnownException(
                          404,
                          String.format(
                              "Could not find a destination specification for destination: %s",
                              destinationIdRequestBody.getDestinationId())));
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    return toDestinationSpecificationRead(destinationConnection);
  }

  private static DestinationSpecificationRead toDestinationSpecificationRead(
      DestinationConnectionSpecification destinationConnectionSpecification) {
    final DestinationSpecificationRead destinationSpecificationRead =
        new DestinationSpecificationRead();
    destinationSpecificationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    destinationSpecificationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    destinationSpecificationRead.setConnectionSpecification(
        destinationConnectionSpecification.getSpecification());

    return destinationSpecificationRead;
  }
}

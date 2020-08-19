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

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;

public class SourceSpecificationsHandler {
  private final ConfigPersistence configPersistence;

  public SourceSpecificationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public SourceSpecificationRead getSourceSpecification(SourceIdRequestBody sourceIdRequestBody) {
    final SourceConnectionSpecification sourceConnection;
    try {
      // todo (cgardens) - this is a shortcoming of rolling our own disk storage. since we are not
      //   querying on a the primary key, we have to list all of the specification objects and then
      //   filter.
      sourceConnection =
          configPersistence
              .getConfigs(
                  PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
                  SourceConnectionSpecification.class)
              .stream()
              .filter(
                  sourceSpecification ->
                      sourceSpecification.getSourceId().equals(sourceIdRequestBody.getSourceId()))
              .findFirst()
              .orElseThrow(
                  () ->
                      new KnownException(
                          404,
                          String.format(
                              "Could not find a source specification for source: %s",
                              sourceIdRequestBody.getSourceId())));
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    return toSourceSpecificationRead(sourceConnection);
  }

  private static SourceSpecificationRead toSourceSpecificationRead(
      SourceConnectionSpecification sourceConnectionSpecification) {
    final SourceSpecificationRead sourceSpecificationRead = new SourceSpecificationRead();
    sourceSpecificationRead.setSourceId(sourceConnectionSpecification.getSourceId());
    sourceSpecificationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    sourceSpecificationRead.setConnectionSpecification(
        sourceConnectionSpecification.getSpecification());

    return sourceSpecificationRead;
  }
}

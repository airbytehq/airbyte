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

package io.airbyte.server.handlers;

import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceSpecificationRead;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.SourceConnectionSpecification;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.errors.KnownException;
import java.io.IOException;

public class SourceSpecificationsHandler {

  private final ConfigRepository configRepository;

  public SourceSpecificationsHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public SourceSpecificationRead getSourceSpecification(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // todo (cgardens) - this is a shortcoming of rolling our own disk storage. since we are not
    // querying on a the primary key, we have to list all of the specification objects and then
    // filter.
    final SourceConnectionSpecification sourceConnection = configRepository.listSourceConnectionSpecifications().stream()
        .filter(sourceSpecification -> sourceSpecification.getSourceId().equals(sourceIdRequestBody.getSourceId()))
        .findFirst()
        .orElseThrow(
            () -> new KnownException(
                404,
                String.format(
                    "Could not find a source specification for source: %s",
                    sourceIdRequestBody.getSourceId())));

    return buildSourceSpecificationRead(sourceConnection);
  }

  private static SourceSpecificationRead buildSourceSpecificationRead(SourceConnectionSpecification scs) {
    return new SourceSpecificationRead()
        .sourceId(scs.getSourceId())
        .sourceSpecificationId(scs.getSourceSpecificationId())
        .documentation(scs.getDocumentation())
        .connectionSpecification(scs.getSpecification());
  }

}

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
import io.dataline.api.model.DestinationRead;
import io.dataline.api.model.DestinationReadList;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

public class DestinationsHandler {

  private final ConfigRepository configRepository;

  public DestinationsHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public DestinationReadList listDestinations()
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationRead> reads = configRepository.listStandardDestinations()
        .stream()
        .map(DestinationsHandler::buildDestinationRead)
        .collect(Collectors.toList());

    return new DestinationReadList().destinations(reads);
  }

  public DestinationRead getDestination(DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationRead(configRepository.getStandardDestination(destinationIdRequestBody.getDestinationId()));
  }

  private static DestinationRead buildDestinationRead(StandardDestination standardDestination) {
    final DestinationRead destinationRead = new DestinationRead();
    destinationRead.setDestinationId(standardDestination.getDestinationId());
    destinationRead.setName(standardDestination.getName());

    return destinationRead;
  }

}

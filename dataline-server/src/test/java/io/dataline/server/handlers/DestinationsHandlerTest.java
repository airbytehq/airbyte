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

import com.google.common.collect.Lists;
import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationRead;
import io.dataline.api.model.DestinationReadList;
import io.dataline.config.ConfigSchema;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DestinationsHandlerTest {

  private ConfigPersistence configPersistence;
  private StandardDestination destination;
  private DestinationsHandler destinationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    destination = generateDestination();
    destinationHandler = new DestinationsHandler(configPersistence);
  }

  private StandardDestination generateDestination() {
    final UUID destinationId = UUID.randomUUID();

    return new StandardDestination()
    .withDestinationId(destinationId)
    .withName("presto");
  }

  @Test
  void testListDestinations() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardDestination destination2 = generateDestination();
    configPersistence.writeConfig(
        ConfigSchema.STANDARD_DESTINATION,
        destination2.getDestinationId().toString(),
        destination2);

    when(configPersistence.listConfigs(
        ConfigSchema.STANDARD_DESTINATION, StandardDestination.class))
            .thenReturn(Lists.newArrayList(destination, destination2));

    DestinationRead expectedDestinationRead1 = new DestinationRead()
    .destinationId(destination.getDestinationId())
    .name(destination.getName());

    DestinationRead expectedDestinationRead2 = new DestinationRead()
    .destinationId(destination2.getDestinationId())
    .name(destination2.getName());

    final DestinationReadList actualDestinationReadList = destinationHandler.listDestinations();

    final Optional<DestinationRead> actualDestinationRead1 =        actualDestinationReadList.getDestinations()
        .stream()
            .filter(
                destinationRead -> destinationRead.getDestinationId().equals(destination.getDestinationId()))
            .findFirst();
    final Optional<DestinationRead> actualDestinationRead2 =        actualDestinationReadList.getDestinations()
        .stream()
            .filter(
                destinationRead -> destinationRead.getDestinationId().equals(destination2.getDestinationId()))
            .findFirst();

    assertTrue(actualDestinationRead1.isPresent());
    assertEquals(expectedDestinationRead1, actualDestinationRead1.get());
    assertTrue(actualDestinationRead2.isPresent());
    assertEquals(expectedDestinationRead2, actualDestinationRead2.get());
  }

  @Test
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_DESTINATION,
        destination.getDestinationId().toString(),
        StandardDestination.class))
            .thenReturn(destination);

    DestinationRead expectedDestinationRead = new DestinationRead()
    .destinationId(destination.getDestinationId())
    .name(destination.getName());

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody()
    .destinationId(destination.getDestinationId());

    final DestinationRead actualDestinationRead =        destinationHandler.getDestination(destinationIdRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);
  }

}

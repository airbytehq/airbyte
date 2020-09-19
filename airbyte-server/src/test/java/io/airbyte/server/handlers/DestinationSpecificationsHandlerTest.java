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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationSpecificationRead;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.helpers.DestinationSpecificationHelpers;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationSpecificationsHandlerTest {

  private ConfigRepository configRepository;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationSpecificationsHandler destinationSpecificationHandler;

  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    destinationConnectionSpecification = DestinationSpecificationHelpers.generateDestinationSpecification();
    destinationSpecificationHandler = new DestinationSpecificationsHandler(configRepository);
  }

  @Test
  void testGetDestinationSpecification() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(configRepository.listDestinationConnectionSpecifications())
        .thenReturn(Lists.newArrayList(destinationConnectionSpecification));

    DestinationSpecificationRead expectedDestinationSpecificationRead = new DestinationSpecificationRead();
    expectedDestinationSpecificationRead.setDestinationId(destinationConnectionSpecification.getDestinationId());
    expectedDestinationSpecificationRead.setDestinationSpecificationId(destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationSpecificationRead.setConnectionSpecification(destinationConnectionSpecification.getSpecification());

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(expectedDestinationSpecificationRead.getDestinationId());

    final DestinationSpecificationRead actualDestinationSpecificationRead =
        destinationSpecificationHandler.getDestinationSpecification(destinationIdRequestBody);

    assertEquals(expectedDestinationSpecificationRead, actualDestinationSpecificationRead);
  }

}

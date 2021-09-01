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

import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class WebBackendDestinationHandlerTest {

  private WebBackendDestinationHandler wbDestinationHandler;

  private DestinationHandler destinationHandler;

  private DestinationRead destinationRead;

  @BeforeEach
  public void setup() throws IOException {
    destinationHandler = mock(DestinationHandler.class);
    wbDestinationHandler = new WebBackendDestinationHandler(destinationHandler, mock(OAuthHandler.class));

    final StandardDestinationDefinition standardDestinationDefinition = DestinationDefinitionHelpers.generateDestination();
    DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    destinationRead = DestinationHelpers.getDestinationRead(destination, standardDestinationDefinition);
  }

  @Test
  public void testWebBackendCreateDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationCreate destinationCreate = new DestinationCreate();
    destinationCreate.setName(destinationRead.getName());
    destinationCreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationCreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationCreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    when(destinationHandler.createDestination(destinationCreate)).thenReturn(destinationRead);

    final DestinationRead actualDestinationRead = wbDestinationHandler.webBackendCreateDestination(destinationCreate);
    assertEquals(destinationRead, actualDestinationRead);
  }

}

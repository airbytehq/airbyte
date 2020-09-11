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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.dataline.api.model.DestinationImplementationCreate;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.DestinationImplementationRead;
import io.dataline.api.model.DestinationImplementationReadList;
import io.dataline.api.model.DestinationImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.json.Jsons;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.commons.json.JsonValidationException;
import io.dataline.server.helpers.DestinationHelpers;
import io.dataline.server.helpers.DestinationSpecificationHelpers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationImplementationsHandlerTest {

  private ConfigRepository configRepository;
  private StandardDestination standardDestination;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationImplementationsHandler destinationImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    validator = mock(IntegrationSchemaValidation.class);
    uuidGenerator = mock(Supplier.class);

    standardDestination = DestinationHelpers.generateDestination();
    destinationConnectionSpecification = DestinationSpecificationHelpers.generateDestinationSpecification(standardDestination.getDestinationId());
    destinationConnectionImplementation = generateDestinationImplementation(
        destinationConnectionSpecification.getDestinationSpecificationId());

    destinationImplementationsHandler = new DestinationImplementationsHandler(configRepository, validator, uuidGenerator);
  }

  private JsonNode getTestImplementationJson() throws IOException {
    final Path path =
        Paths.get("../dataline-server/src/test/resources/json/TestImplementation.json");

    return Jsons.deserialize(Files.readString(path));
  }

  private DestinationConnectionImplementation generateDestinationImplementation(UUID destinationSpecificationId)
      throws IOException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID destinationImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    return new DestinationConnectionImplementation()
        .withName("my db2 instance")
        .withWorkspaceId(workspaceId)
        .withDestinationSpecificationId(destinationSpecificationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withConfiguration(implementationJson);
  }

  @Test
  void testCreateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnectionImplementation.getDestinationImplementationId());

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(configRepository.getDestinationConnectionSpecification(destinationConnectionImplementation.getDestinationSpecificationId()))
        .thenReturn(destinationConnectionSpecification);

    when(configRepository.getStandardDestination(destinationConnectionSpecification.getDestinationId()))
        .thenReturn(standardDestination);

    final DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate()
        .name(destinationConnectionImplementation.getName())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationSpecificationId(destinationConnectionSpecification.getDestinationSpecificationId())
        .connectionConfiguration(getTestImplementationJson());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(destinationConnectionSpecification.getDestinationId())
        .destinationSpecificationId(destinationConnectionSpecification.getDestinationSpecificationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(getTestImplementationJson())
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(validator)
        .validateConfig(
            destinationConnectionSpecification,
            destinationConnectionImplementation.getConfiguration());

    verify(configRepository).writeDestinationConnectionImplementation(destinationConnectionImplementation);
  }

  @Test
  void testUpdateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = destinationConnectionImplementation.getConfiguration();

    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation = Jsons.clone(destinationConnectionImplementation)
        .withConfiguration(newConfiguration);

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    when(configRepository.getDestinationConnectionSpecification(destinationConnectionImplementation.getDestinationSpecificationId()))
        .thenReturn(destinationConnectionSpecification);

    when(configRepository.getStandardDestination(destinationConnectionSpecification.getDestinationId()))
        .thenReturn(standardDestination);

    final DestinationImplementationUpdate destinationImplementationUpdate = new DestinationImplementationUpdate()
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .name(destinationConnectionImplementation.getName())
        .connectionConfiguration(newConfiguration);

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.updateDestinationImplementation(destinationImplementationUpdate);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(destinationConnectionSpecification.getDestinationId())
        .destinationSpecificationId(destinationConnectionSpecification.getDestinationSpecificationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(newConfiguration)
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(configRepository).writeDestinationConnectionImplementation(expectedDestinationConnectionImplementation);
  }

  @Test
  void testGetDestinationImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(configRepository.getDestinationConnectionSpecification(destinationConnectionImplementation.getDestinationSpecificationId()))
        .thenReturn(destinationConnectionSpecification);

    when(configRepository.getStandardDestination(destinationConnectionSpecification.getDestinationId()))
        .thenReturn(standardDestination);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(destinationConnectionSpecification.getDestinationId())
        .destinationSpecificationId(destinationConnectionImplementation.getDestinationSpecificationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody()
        .destinationImplementationId(expectedDestinationImplementationRead.getDestinationImplementationId());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void testListDestinationImplementationsForWorkspace()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);
    when(configRepository.listDestinationConnectionImplementations())
        .thenReturn(Lists.newArrayList(destinationConnectionImplementation));
    when(configRepository.getDestinationConnectionSpecification(destinationConnectionImplementation.getDestinationSpecificationId()))
        .thenReturn(destinationConnectionSpecification);
    when(configRepository.getStandardDestination(destinationConnectionSpecification.getDestinationId()))
        .thenReturn(standardDestination);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(destinationConnectionSpecification.getDestinationId())
        .destinationSpecificationId(destinationConnectionImplementation.getDestinationSpecificationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(destinationConnectionImplementation.getWorkspaceId());

    final DestinationImplementationReadList actualDestinationImplementationRead =
        destinationImplementationsHandler.listDestinationImplementationsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        expectedDestinationImplementationRead,
        actualDestinationImplementationRead.getDestinations().get(0));
  }

}

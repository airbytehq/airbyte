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
import com.google.common.collect.Sets;
import io.dataline.api.model.DestinationImplementationCreate;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.DestinationImplementationRead;
import io.dataline.api.model.DestinationImplementationReadList;
import io.dataline.api.model.DestinationImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.json.Jsons;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
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

  private ConfigPersistence configPersistence;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationImplementationsHandler destinationImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configPersistence = mock(ConfigPersistence.class);
    validator = mock(IntegrationSchemaValidation.class);
    uuidGenerator = mock(Supplier.class);

    destinationConnectionSpecification =
        DestinationSpecificationHelpers.generateDestinationSpecification();
    destinationConnectionImplementation =
        generateDestinationImplementation(
            destinationConnectionSpecification.getDestinationSpecificationId());

    destinationImplementationsHandler =
        new DestinationImplementationsHandler(configPersistence, validator, uuidGenerator);
  }

  private String getTestImplementationJson() throws IOException {
    final Path path =
        Paths.get("../dataline-server/src/test/resources/json/TestImplementation.json");

    return Files.readString(path);
  }

  private DestinationConnectionImplementation generateDestinationImplementation(UUID destinationSpecificationId)
      throws IOException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID destinationImplementationId = UUID.randomUUID();

    String implementationJson = getTestImplementationJson();

    final DestinationConnectionImplementation destinationConnectionImplementation =
        new DestinationConnectionImplementation();
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfigurationJson(implementationJson);

    return destinationConnectionImplementation;
  }

  @Test
  void testCreateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnectionImplementation.getDestinationImplementationId());

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationConnectionImplementation.getDestinationImplementationId().toString(),
        DestinationConnectionImplementation.class))
            .thenReturn(destinationConnectionImplementation);

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
        destinationConnectionImplementation.getDestinationSpecificationId().toString(),
        DestinationConnectionSpecification.class))
            .thenReturn(destinationConnectionSpecification);

    final DestinationImplementationCreate destinationImplementationCreate =
        new DestinationImplementationCreate();
    destinationImplementationCreate.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    destinationImplementationCreate.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    destinationImplementationCreate.setConnectionConfiguration(
        getTestImplementationJson().toString());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.createDestinationImplementation(
            destinationImplementationCreate);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        getTestImplementationJson().toString());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(validator)
        .validateDestinationConnectionConfiguration(
            destinationConnectionSpecification.getDestinationSpecificationId(),
            destinationConnectionImplementation.getConfigurationJson());

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            destinationConnectionImplementation);
  }

  @Test
  void testUpdateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException {
    final JsonNode newConfiguration =
        Jsons.deserialize(destinationConnectionImplementation.getConfigurationJson());

    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation =
        new DestinationConnectionImplementation();
    expectedDestinationConnectionImplementation.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationConnectionImplementation.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationConnectionImplementation.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationConnectionImplementation.setConfigurationJson(newConfiguration.toString());

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationConnectionImplementation.getDestinationImplementationId().toString(),
        DestinationConnectionImplementation.class))
            .thenReturn(destinationConnectionImplementation)
            .thenReturn(expectedDestinationConnectionImplementation);

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
        destinationConnectionImplementation.getDestinationSpecificationId().toString(),
        DestinationConnectionSpecification.class))
            .thenReturn(destinationConnectionSpecification);

    final DestinationImplementationUpdate destinationImplementationUpdate =
        new DestinationImplementationUpdate();
    destinationImplementationUpdate.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    destinationImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.updateDestinationImplementation(
            destinationImplementationUpdate);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            expectedDestinationConnectionImplementation);
  }

  @Test
  void testGetDestinationImplementation() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationConnectionImplementation.getDestinationImplementationId().toString(),
        DestinationConnectionImplementation.class))
            .thenReturn(destinationConnectionImplementation);

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
        destinationConnectionImplementation.getDestinationSpecificationId().toString(),
        DestinationConnectionSpecification.class))
            .thenReturn(destinationConnectionSpecification);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfigurationJson());

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody =
        new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(
        expectedDestinationImplementationRead.getDestinationImplementationId());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(
            destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void testListDestinationImplementationsForWorkspace()
      throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfigs(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        DestinationConnectionImplementation.class))
            .thenReturn(Sets.newHashSet(destinationConnectionImplementation));

    when(configPersistence.getConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
        destinationConnectionImplementation.getDestinationSpecificationId().toString(),
        DestinationConnectionSpecification.class))
            .thenReturn(destinationConnectionSpecification);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfigurationJson());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(destinationConnectionImplementation.getWorkspaceId());

    final DestinationImplementationReadList actualDestinationImplementationRead =
        destinationImplementationsHandler.listDestinationImplementationsForWorkspace(
            workspaceIdRequestBody);

    assertEquals(
        expectedDestinationImplementationRead,
        actualDestinationImplementationRead.getDestinations().get(0));
  }

}

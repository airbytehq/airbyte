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
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.json.Jsons;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.SourceImplementationHelpers;
import io.dataline.server.helpers.SourceSpecificationHelpers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceImplementationsHandlerTest {

  private ConfigPersistence configPersistence;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceConnectionImplementation sourceConnectionImplementation;
  private SourceImplementationsHandler sourceImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configPersistence = mock(ConfigPersistence.class);
    validator = mock(IntegrationSchemaValidation.class);
    uuidGenerator = mock(Supplier.class);

    sourceConnectionSpecification = SourceSpecificationHelpers.generateSourceSpecification();
    sourceConnectionImplementation =
        SourceImplementationHelpers.generateSourceImplementation(
            sourceConnectionSpecification.getSourceSpecificationId());

    sourceImplementationsHandler =
        new SourceImplementationsHandler(configPersistence, validator, uuidGenerator);
  }

  @Test
  void testCreateSourceImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(sourceConnectionImplementation.getSourceImplementationId());

    when(configPersistence.getConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation);

    final SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());
    sourceImplementationCreate.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    sourceImplementationCreate.setConnectionConfiguration(
        SourceImplementationHelpers.getTestImplementationJson());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        SourceImplementationHelpers.getTestImplementationJson());

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(validator)
        .validateSourceConnectionConfiguration(
            sourceConnectionSpecification.getSourceSpecificationId(),
            sourceConnectionImplementation.getConfigurationJson());

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            sourceConnectionImplementation);
  }

  @Test
  void testUpdateSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    final JsonNode newConfiguration =
        Jsons.deserialize(sourceConnectionImplementation.getConfigurationJson());
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation =
        new SourceConnectionImplementation();
    expectedSourceConnectionImplementation.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceConnectionImplementation.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceConnectionImplementation.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceConnectionImplementation.setConfigurationJson(newConfiguration.toString());
    expectedSourceConnectionImplementation.setTombstone(false);

    when(configPersistence.getConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation)
            .thenReturn(expectedSourceConnectionImplementation);

    final SourceImplementationUpdate sourceImplementationUpdate = new SourceImplementationUpdate();
    sourceImplementationUpdate.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            expectedSourceConnectionImplementation);
  }

  @Test
  void testGetSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        sourceConnectionImplementation.getConfigurationJson());

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
        new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(
        expectedSourceImplementationRead.getSourceImplementationId());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);
  }

  @Test
  void testListSourceImplementationsForWorkspace() throws JsonValidationException {
    when(configPersistence.getConfigs(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        SourceConnectionImplementation.class))
            .thenReturn(Sets.newHashSet(sourceConnectionImplementation));

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        sourceConnectionImplementation.getConfigurationJson());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());

    final SourceImplementationReadList actualSourceImplementationRead =
        sourceImplementationsHandler.listSourceImplementationsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        expectedSourceImplementationRead, actualSourceImplementationRead.getSources().get(0));
  }

  @Test
  void testDeleteSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    final JsonNode newConfiguration =
        Jsons.deserialize(sourceConnectionImplementation.getConfigurationJson());
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation =
        new SourceConnectionImplementation();
    expectedSourceConnectionImplementation.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceConnectionImplementation.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceConnectionImplementation.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceConnectionImplementation.setConfigurationJson(
        sourceConnectionImplementation.getConfigurationJson());
    expectedSourceConnectionImplementation.setTombstone(true);

    when(configPersistence.getConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation)
            .thenReturn(expectedSourceConnectionImplementation);

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
        new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());

    sourceImplementationsHandler.deleteSourceImplementation(sourceImplementationIdRequestBody);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            expectedSourceConnectionImplementation);
  }

}

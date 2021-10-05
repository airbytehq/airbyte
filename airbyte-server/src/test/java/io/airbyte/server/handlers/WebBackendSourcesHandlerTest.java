/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WebBackendSourcesHandlerTest {

  private SourceHandler sourceHandler;
  private ConfigRepository configRepository;
  private WebBackendSourcesHandler webBackendSourcesHandler;
  private TrackingClient trackingClient;

  @BeforeEach
  public void setup() throws JsonValidationException, ConfigNotFoundException, IOException {
    sourceHandler = mock(SourceHandler.class);
    configRepository = mock(ConfigRepository.class);
    trackingClient = mock(TrackingClient.class);
    webBackendSourcesHandler = new WebBackendSourcesHandler(sourceHandler, configRepository, trackingClient);
    when(configRepository.getStandardSourceDefinition(any())).thenReturn(new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("test")
        .withDockerImageTag("dev"));
  }

  @Test
  public void testWebBackendCreateSourceEmptyOAuthParameters() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceDefinitionId = UUID.randomUUID();
    final SourceConnection sourceConnection = SourceHelpers.generateSource(sourceDefinitionId);
    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceConnection.getName())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(sourceDefinitionId)
        .connectionConfiguration(sourceConnection.getConfiguration());
    webBackendSourcesHandler.webBackendCreateSource(Jsons.clone(sourceCreate));
    verify(sourceHandler).createSource(sourceCreate);
    assertNoTracking();
  }

  @Test
  public void testWebBackendCreateSourceWithMaskedOAuthParameters() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceDefinitionId = UUID.randomUUID();
    final SourceConnection sourceConnection = SourceHelpers.generateSource(sourceDefinitionId);
    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceConnection.getName())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(sourceDefinitionId)
        .connectionConfiguration(sourceConnection.getConfiguration());
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(sourceDefinitionId)
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(ImmutableMap.<String, String>builder()
                .put("api_secret", "mysecret")
                .put("api_client", UUID.randomUUID().toString())
                .build()))));
    final SourceCreate expectedSourceCreate = Jsons.clone(sourceCreate);
    ((ObjectNode) expectedSourceCreate.getConnectionConfiguration())
        .put("api_secret", OAuthConfigSupplier.SECRET_MASK)
        .put("api_client", OAuthConfigSupplier.SECRET_MASK);
    webBackendSourcesHandler.webBackendCreateSource(Jsons.clone(sourceCreate));
    verify(sourceHandler).createSource(expectedSourceCreate);
    assertNoTracking();
  }

  private void assertNoTracking() {
    verify(trackingClient, times(0)).track(any(), anyString(), anyMap());
  }

}

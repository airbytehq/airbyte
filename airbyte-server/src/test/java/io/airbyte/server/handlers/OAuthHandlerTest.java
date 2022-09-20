/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

class OAuthHandlerTest {

  private ConfigRepository configRepository;
  private OAuthHandler handler;
  private TrackingClient trackingClient;
  private HttpClient httpClient;
  private static final String CLIENT_ID = "123";
  private static final String CLIENT_ID_KEY = "client_id";
  private static final String CLIENT_SECRET_KEY = "client_secret";
  private static final String CLIENT_SECRET = "hunter2";

  @BeforeEach
  public void init() {
    configRepository = Mockito.mock(ConfigRepository.class);
    trackingClient = mock(TrackingClient.class);
    httpClient = Mockito.mock(HttpClient.class);
    handler = new OAuthHandler(configRepository, httpClient, trackingClient);
  }

  @Test
  void setSourceInstancewideOauthParams() throws JsonValidationException, IOException {
    final UUID sourceDefId = UUID.randomUUID();
    final Map<String, Object> params = new HashMap<>();
    params.put(CLIENT_ID_KEY, CLIENT_ID);
    params.put(CLIENT_SECRET_KEY, CLIENT_SECRET);

    final SetInstancewideSourceOauthParamsRequestBody actualRequest = new SetInstancewideSourceOauthParamsRequestBody()
        .sourceDefinitionId(sourceDefId)
        .params(params);

    handler.setSourceInstancewideOauthParams(actualRequest);

    final ArgumentCaptor<SourceOAuthParameter> argument = ArgumentCaptor.forClass(SourceOAuthParameter.class);
    Mockito.verify(configRepository).writeSourceOAuthParam(argument.capture());
    assertEquals(Jsons.jsonNode(params), argument.getValue().getConfiguration());
    assertEquals(sourceDefId, argument.getValue().getSourceDefinitionId());
  }

  @Test
  void resetSourceInstancewideOauthParams() throws JsonValidationException, IOException {
    final UUID sourceDefId = UUID.randomUUID();
    final Map<String, Object> firstParams = new HashMap<>();
    firstParams.put(CLIENT_ID_KEY, CLIENT_ID);
    firstParams.put(CLIENT_SECRET_KEY, CLIENT_SECRET);
    final SetInstancewideSourceOauthParamsRequestBody firstRequest = new SetInstancewideSourceOauthParamsRequestBody()
        .sourceDefinitionId(sourceDefId)
        .params(firstParams);
    handler.setSourceInstancewideOauthParams(firstRequest);

    final UUID oauthParameterId = UUID.randomUUID();
    when(configRepository.getSourceOAuthParamByDefinitionIdOptional(null, sourceDefId))
        .thenReturn(Optional.of(new SourceOAuthParameter().withOauthParameterId(oauthParameterId)));

    final Map<String, Object> secondParams = new HashMap<>();
    secondParams.put(CLIENT_ID_KEY, "456");
    secondParams.put(CLIENT_SECRET_KEY, "hunter3");
    final SetInstancewideSourceOauthParamsRequestBody secondRequest = new SetInstancewideSourceOauthParamsRequestBody()
        .sourceDefinitionId(sourceDefId)
        .params(secondParams);
    handler.setSourceInstancewideOauthParams(secondRequest);

    final ArgumentCaptor<SourceOAuthParameter> argument = ArgumentCaptor.forClass(SourceOAuthParameter.class);
    Mockito.verify(configRepository, Mockito.times(2)).writeSourceOAuthParam(argument.capture());
    final List<SourceOAuthParameter> capturedValues = argument.getAllValues();
    assertEquals(Jsons.jsonNode(firstParams), capturedValues.get(0).getConfiguration());
    assertEquals(Jsons.jsonNode(secondParams), capturedValues.get(1).getConfiguration());
    assertEquals(sourceDefId, capturedValues.get(0).getSourceDefinitionId());
    assertEquals(sourceDefId, capturedValues.get(1).getSourceDefinitionId());
    assertEquals(oauthParameterId, capturedValues.get(1).getOauthParameterId());
  }

  @Test
  void setDestinationInstancewideOauthParams() throws JsonValidationException, IOException {
    final UUID destinationDefId = UUID.randomUUID();
    final Map<String, Object> params = new HashMap<>();
    params.put(CLIENT_ID_KEY, CLIENT_ID);
    params.put(CLIENT_SECRET_KEY, CLIENT_SECRET);

    final SetInstancewideDestinationOauthParamsRequestBody actualRequest = new SetInstancewideDestinationOauthParamsRequestBody()
        .destinationDefinitionId(destinationDefId)
        .params(params);

    handler.setDestinationInstancewideOauthParams(actualRequest);

    final ArgumentCaptor<DestinationOAuthParameter> argument = ArgumentCaptor.forClass(DestinationOAuthParameter.class);
    Mockito.verify(configRepository).writeDestinationOAuthParam(argument.capture());
    assertEquals(Jsons.jsonNode(params), argument.getValue().getConfiguration());
    assertEquals(destinationDefId, argument.getValue().getDestinationDefinitionId());
  }

  @Test
  void resetDestinationInstancewideOauthParams() throws JsonValidationException, IOException {
    final UUID destinationDefId = UUID.randomUUID();
    final Map<String, Object> firstParams = new HashMap<>();
    firstParams.put(CLIENT_ID_KEY, CLIENT_ID);
    firstParams.put(CLIENT_SECRET_KEY, CLIENT_SECRET);
    final SetInstancewideDestinationOauthParamsRequestBody firstRequest = new SetInstancewideDestinationOauthParamsRequestBody()
        .destinationDefinitionId(destinationDefId)
        .params(firstParams);
    handler.setDestinationInstancewideOauthParams(firstRequest);

    final UUID oauthParameterId = UUID.randomUUID();
    when(configRepository.getDestinationOAuthParamByDefinitionIdOptional(null, destinationDefId))
        .thenReturn(Optional.of(new DestinationOAuthParameter().withOauthParameterId(oauthParameterId)));

    final Map<String, Object> secondParams = new HashMap<>();
    secondParams.put(CLIENT_ID_KEY, "456");
    secondParams.put(CLIENT_SECRET_KEY, "hunter3");
    final SetInstancewideDestinationOauthParamsRequestBody secondRequest = new SetInstancewideDestinationOauthParamsRequestBody()
        .destinationDefinitionId(destinationDefId)
        .params(secondParams);
    handler.setDestinationInstancewideOauthParams(secondRequest);

    final ArgumentCaptor<DestinationOAuthParameter> argument = ArgumentCaptor.forClass(DestinationOAuthParameter.class);
    Mockito.verify(configRepository, Mockito.times(2)).writeDestinationOAuthParam(argument.capture());
    final List<DestinationOAuthParameter> capturedValues = argument.getAllValues();
    assertEquals(Jsons.jsonNode(firstParams), capturedValues.get(0).getConfiguration());
    assertEquals(Jsons.jsonNode(secondParams), capturedValues.get(1).getConfiguration());
    assertEquals(destinationDefId, capturedValues.get(0).getDestinationDefinitionId());
    assertEquals(destinationDefId, capturedValues.get(1).getDestinationDefinitionId());
    assertEquals(oauthParameterId, capturedValues.get(1).getOauthParameterId());
  }

}

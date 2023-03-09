/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
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
  private SecretsRepositoryReader secretsRepositoryReader;
  private static final String CLIENT_ID = "123";
  private static final String CLIENT_ID_KEY = "client_id";
  private static final String CLIENT_SECRET_KEY = "client_secret";
  private static final String CLIENT_SECRET = "hunter2";

  @BeforeEach
  public void init() {
    configRepository = Mockito.mock(ConfigRepository.class);
    trackingClient = mock(TrackingClient.class);
    httpClient = Mockito.mock(HttpClient.class);
    secretsRepositoryReader = mock(SecretsRepositoryReader.class);
    handler = new OAuthHandler(configRepository, httpClient, trackingClient, secretsRepositoryReader);
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

  @Test
  void testBuildJsonPathFromOAuthFlowInitParameters() {
    final Map<String, List<String>> input = Map.ofEntries(
        Map.entry("field1", List.of("1")),
        Map.entry("field2", List.of("2", "3")));

    final Map<String, String> expected = Map.ofEntries(
        Map.entry("field1", "$.1"),
        Map.entry("field2", "$.2.3"));

    assertEquals(expected, handler.buildJsonPathFromOAuthFlowInitParameters(input));
  }

  @Test
  void testGetOAuthInputConfiguration() {
    final JsonNode hydratedConfig = Jsons.deserialize(
        """
        {
          "field1": "1",
          "field2": "2",
          "field3": {
            "field3_1": "3_1",
            "field3_2": "3_2"
          }
        }
        """);

    final Map<String, String> pathsToGet = Map.ofEntries(
        Map.entry("field1", "$.field1"),
        Map.entry("field3_1", "$.field3.field3_1"),
        Map.entry("field3_2", "$.field3.field3_2"),
        Map.entry("field4", "$.someNonexistentField"));

    final JsonNode expected = Jsons.deserialize(
        """
        {
          "field1": "1",
          "field3_1": "3_1",
          "field3_2": "3_2"
        }
        """);

    assertEquals(expected, handler.getOAuthInputConfiguration(hydratedConfig, pathsToGet));
  }

  @Test
  void testGetOauthFromDBIfNeeded() {
    final JsonNode fromInput = Jsons.deserialize(
        """
        {
          "testMask": "**********",
          "testNotMask": "this",
          "testOtherType": true
        }
        """);

    final JsonNode fromDb = Jsons.deserialize(
        """
        {
          "testMask": "mask",
          "testNotMask": "notThis",
          "testOtherType": true
        }
        """);

    final JsonNode expected = Jsons.deserialize(
        """
        {
          "testMask": "mask",
          "testNotMask": "this",
          "testOtherType": true
        }
        """);

    assertEquals(expected, handler.getOauthFromDBIfNeeded(fromDb, fromInput));
  }

}

/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.CompleteSourceOauthRequest;
import io.airbyte.api.model.DestinationOauthConsentRequest;
import io.airbyte.api.model.OAuthConsentRead;
import io.airbyte.api.model.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.SourceOauthConsentRequest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.scheduler.persistence.job_tracker.TrackingMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;

public class OAuthHandler {

  private final ConfigRepository configRepository;
  private final OAuthImplementationFactory oAuthImplementationFactory;
  private final TrackingClient trackingClient;

  public OAuthHandler(ConfigRepository configRepository, TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.oAuthImplementationFactory = new OAuthImplementationFactory(configRepository);
    this.trackingClient = trackingClient;
  }

  public OAuthConsentRead getSourceOAuthConsent(SourceOauthConsentRequest sourceDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation = getSourceOAuthFlowImplementation(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthConsentRead result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
        sourceDefinitionIdRequestBody.getWorkspaceId(),
        sourceDefinitionIdRequestBody.getSourceDefinitionId(),
        sourceDefinitionIdRequestBody.getRedirectUrl()));
    trackingClient.track(sourceDefinitionIdRequestBody.getWorkspaceId(), "OAuth Consent - Backend", metadata);
    return result;
  }

  public OAuthConsentRead getDestinationOAuthConsent(DestinationOauthConsentRequest destinationDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation =
        getDestinationOAuthFlowImplementation(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthConsentRead result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
        destinationDefinitionIdRequestBody.getWorkspaceId(),
        destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
        destinationDefinitionIdRequestBody.getRedirectUrl()));
    trackingClient.track(destinationDefinitionIdRequestBody.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    return result;
  }

  public Map<String, Object> completeSourceOAuth(CompleteSourceOauthRequest oauthSourceRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation = getSourceOAuthFlowImplementation(oauthSourceRequestBody.getSourceDefinitionId());
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(oauthSourceRequestBody.getSourceDefinitionId());
    final Map<String, Object> result = oAuthFlowImplementation.completeSourceOAuth(
        oauthSourceRequestBody.getWorkspaceId(),
        oauthSourceRequestBody.getSourceDefinitionId(),
        oauthSourceRequestBody.getQueryParams(),
        oauthSourceRequestBody.getRedirectUrl());
    trackingClient.track(oauthSourceRequestBody.getWorkspaceId(), "OAuth Flow - Backend", metadata);
    return result;
  }

  public Map<String, Object> completeDestinationOAuth(CompleteDestinationOAuthRequest oauthDestinationRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation =
        getDestinationOAuthFlowImplementation(oauthDestinationRequestBody.getDestinationDefinitionId());
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(oauthDestinationRequestBody.getDestinationDefinitionId());
    final Map<String, Object> result = oAuthFlowImplementation.completeDestinationOAuth(
        oauthDestinationRequestBody.getWorkspaceId(),
        oauthDestinationRequestBody.getDestinationDefinitionId(),
        oauthDestinationRequestBody.getQueryParams(),
        oauthDestinationRequestBody.getRedirectUrl());
    trackingClient.track(oauthDestinationRequestBody.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    return result;
  }

  public void setSourceInstancewideOauthParams(SetInstancewideSourceOauthParamsRequestBody requestBody) throws JsonValidationException, IOException {
    final SourceOAuthParameter param = configRepository
        .getSourceOAuthParamByDefinitionIdOptional(null, requestBody.getSourceDefinitionId())
        .orElseGet(() -> new SourceOAuthParameter().withOauthParameterId(UUID.randomUUID()))
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withSourceDefinitionId(requestBody.getSourceDefinitionId());
    configRepository.writeSourceOAuthParam(param);
  }

  public void setDestinationInstancewideOauthParams(SetInstancewideDestinationOauthParamsRequestBody requestBody)
      throws JsonValidationException, IOException {
    final DestinationOAuthParameter param = configRepository
        .getDestinationOAuthParamByDefinitionIdOptional(null, requestBody.getDestinationDefinitionId())
        .orElseGet(() -> new DestinationOAuthParameter().withOauthParameterId(UUID.randomUUID()))
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withDestinationDefinitionId(requestBody.getDestinationDefinitionId());
    configRepository.writeDestinationOAuthParam(param);
  }

  private OAuthFlowImplementation getSourceOAuthFlowImplementation(UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition standardSourceDefinition = configRepository
        .getStandardSourceDefinition(sourceDefinitionId);
    return oAuthImplementationFactory.create(standardSourceDefinition.getDockerRepository());
  }

  private OAuthFlowImplementation getDestinationOAuthFlowImplementation(UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition standardDestinationDefinition = configRepository
        .getStandardDestinationDefinition(destinationDefinitionId);
    return oAuthImplementationFactory.create(standardDestinationDefinition.getDockerRepository());
  }

  private ImmutableMap<String, Object> generateSourceMetadata(final UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    return TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
  }

  private ImmutableMap<String, Object> generateDestinationMetadata(final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    return TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
  }

}

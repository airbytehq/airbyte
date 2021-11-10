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
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OAuthHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(OAuthHandler.class);

  private final ConfigRepository configRepository;
  private final OAuthImplementationFactory oAuthImplementationFactory;
  private final TrackingClient trackingClient;

  public OAuthHandler(final ConfigRepository configRepository, final HttpClient httpClient, final TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.oAuthImplementationFactory = new OAuthImplementationFactory(configRepository, httpClient);
    this.trackingClient = trackingClient;
  }

  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation =
        oAuthImplementationFactory.create(sourceDefinition, sourceDefinitionIdRequestBody.getWorkspaceId());
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthConsentRead result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
        sourceDefinitionIdRequestBody.getWorkspaceId(),
        sourceDefinitionIdRequestBody.getSourceDefinitionId(),
        sourceDefinitionIdRequestBody.getRedirectUrl()));
    try {
      trackingClient.track(sourceDefinitionIdRequestBody.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
    return result;
  }

  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation =
        oAuthImplementationFactory.create(destinationDefinition, destinationDefinitionIdRequestBody.getWorkspaceId());
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthConsentRead result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
        destinationDefinitionIdRequestBody.getWorkspaceId(),
        destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
        destinationDefinitionIdRequestBody.getRedirectUrl()));
    try {
      trackingClient.track(destinationDefinitionIdRequestBody.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
    return result;
  }

  public Map<String, Object> completeSourceOAuth(final CompleteSourceOauthRequest oauthSourceRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(oauthSourceRequestBody.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation =
        oAuthImplementationFactory.create(sourceDefinition, oauthSourceRequestBody.getWorkspaceId());
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(oauthSourceRequestBody.getSourceDefinitionId());
    final Map<String, Object> result = oAuthFlowImplementation.completeSourceOAuth(
        oauthSourceRequestBody.getWorkspaceId(),
        oauthSourceRequestBody.getSourceDefinitionId(),
        oauthSourceRequestBody.getQueryParams(),
        oauthSourceRequestBody.getRedirectUrl());
    try {
      trackingClient.track(oauthSourceRequestBody.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
    return result;
  }

  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest oauthDestinationRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(oauthDestinationRequestBody.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation =
        oAuthImplementationFactory.create(destinationDefinition, oauthDestinationRequestBody.getWorkspaceId());
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(oauthDestinationRequestBody.getDestinationDefinitionId());
    final Map<String, Object> result = oAuthFlowImplementation.completeDestinationOAuth(
        oauthDestinationRequestBody.getWorkspaceId(),
        oauthDestinationRequestBody.getDestinationDefinitionId(),
        oauthDestinationRequestBody.getQueryParams(),
        oauthDestinationRequestBody.getRedirectUrl());
    try {
      trackingClient.track(oauthDestinationRequestBody.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
    return result;
  }

  public void setSourceInstancewideOauthParams(final SetInstancewideSourceOauthParamsRequestBody requestBody)
      throws JsonValidationException, IOException {
    final SourceOAuthParameter param = configRepository
        .getSourceOAuthParamByDefinitionIdOptional(null, requestBody.getSourceDefinitionId())
        .orElseGet(() -> new SourceOAuthParameter().withOauthParameterId(UUID.randomUUID()))
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withSourceDefinitionId(requestBody.getSourceDefinitionId());
    configRepository.writeSourceOAuthParam(param);
  }

  public void setDestinationInstancewideOauthParams(final SetInstancewideDestinationOauthParamsRequestBody requestBody)
      throws JsonValidationException, IOException {
    final DestinationOAuthParameter param = configRepository
        .getDestinationOAuthParamByDefinitionIdOptional(null, requestBody.getDestinationDefinitionId())
        .orElseGet(() -> new DestinationOAuthParameter().withOauthParameterId(UUID.randomUUID()))
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withDestinationDefinitionId(requestBody.getDestinationDefinitionId());
    configRepository.writeDestinationOAuthParam(param);
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

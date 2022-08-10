/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.generated.CompleteSourceOauthRequest;
import io.airbyte.api.model.generated.DestinationOauthConsentRequest;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.generated.SourceOauthConsentRequest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
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
  private static final String ERROR_MESSAGE = "failed while reporting usage.";

  private final ConfigRepository configRepository;
  private final OAuthImplementationFactory oAuthImplementationFactory;
  private final TrackingClient trackingClient;

  public OAuthHandler(final ConfigRepository configRepository,
                      final HttpClient httpClient,
                      final TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.oAuthImplementationFactory = new OAuthImplementationFactory(configRepository, httpClient);
    this.trackingClient = trackingClient;
  }

  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(sourceDefinition);
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
          sourceDefinitionIdRequestBody.getWorkspaceId(),
          sourceDefinitionIdRequestBody.getSourceDefinitionId(),
          sourceDefinitionIdRequestBody.getRedirectUrl(),
          sourceDefinitionIdRequestBody.getoAuthInputConfiguration(),
          spec.getAdvancedAuth().getOauthConfigSpecification()));
    } else {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
          sourceDefinitionIdRequestBody.getWorkspaceId(),
          sourceDefinitionIdRequestBody.getSourceDefinitionId(),
          sourceDefinitionIdRequestBody.getRedirectUrl(), Jsons.emptyObject(), null));
    }
    try {
      trackingClient.track(sourceDefinitionIdRequestBody.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(destinationDefinition);
    final ConnectorSpecification spec = destinationDefinition.getSpec();
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
          destinationDefinitionIdRequestBody.getWorkspaceId(),
          destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
          destinationDefinitionIdRequestBody.getRedirectUrl(),
          destinationDefinitionIdRequestBody.getoAuthInputConfiguration(),
          spec.getAdvancedAuth().getOauthConfigSpecification()));
    } else {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
          destinationDefinitionIdRequestBody.getWorkspaceId(),
          destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
          destinationDefinitionIdRequestBody.getRedirectUrl(), Jsons.emptyObject(), null));
    }
    try {
      trackingClient.track(destinationDefinitionIdRequestBody.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public Map<String, Object> completeSourceOAuth(final CompleteSourceOauthRequest oauthSourceRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(oauthSourceRequestBody.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(sourceDefinition);
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    final ImmutableMap<String, Object> metadata = generateSourceMetadata(oauthSourceRequestBody.getSourceDefinitionId());
    final Map<String, Object> result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      result = oAuthFlowImplementation.completeSourceOAuth(
          oauthSourceRequestBody.getWorkspaceId(),
          oauthSourceRequestBody.getSourceDefinitionId(),
          oauthSourceRequestBody.getQueryParams(),
          oauthSourceRequestBody.getRedirectUrl(),
          oauthSourceRequestBody.getoAuthInputConfiguration(),
          spec.getAdvancedAuth().getOauthConfigSpecification());
    } else {
      // deprecated but this path is kept for connectors that don't define OAuth Spec yet
      result = oAuthFlowImplementation.completeSourceOAuth(
          oauthSourceRequestBody.getWorkspaceId(),
          oauthSourceRequestBody.getSourceDefinitionId(),
          oauthSourceRequestBody.getQueryParams(),
          oauthSourceRequestBody.getRedirectUrl());
    }
    try {
      trackingClient.track(oauthSourceRequestBody.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest oauthDestinationRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(oauthDestinationRequestBody.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(destinationDefinition);
    final ConnectorSpecification spec = destinationDefinition.getSpec();
    final ImmutableMap<String, Object> metadata = generateDestinationMetadata(oauthDestinationRequestBody.getDestinationDefinitionId());
    final Map<String, Object> result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      result = oAuthFlowImplementation.completeDestinationOAuth(
          oauthDestinationRequestBody.getWorkspaceId(),
          oauthDestinationRequestBody.getDestinationDefinitionId(),
          oauthDestinationRequestBody.getQueryParams(),
          oauthDestinationRequestBody.getRedirectUrl(),
          oauthDestinationRequestBody.getoAuthInputConfiguration(),
          spec.getAdvancedAuth().getOauthConfigSpecification());
    } else {
      // deprecated but this path is kept for connectors that don't define OAuth Spec yet
      result = oAuthFlowImplementation.completeDestinationOAuth(
          oauthDestinationRequestBody.getWorkspaceId(),
          oauthDestinationRequestBody.getDestinationDefinitionId(),
          oauthDestinationRequestBody.getQueryParams(),
          oauthDestinationRequestBody.getRedirectUrl());
    }
    try {
      trackingClient.track(oauthDestinationRequestBody.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
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
    // TODO validate requestBody.getParams() against
    // spec.getAdvancedAuth().getOauthConfigSpecification().getCompleteOauthServerInputSpecification()
    configRepository.writeSourceOAuthParam(param);
  }

  public void setDestinationInstancewideOauthParams(final SetInstancewideDestinationOauthParamsRequestBody requestBody)
      throws JsonValidationException, IOException {
    final DestinationOAuthParameter param = configRepository
        .getDestinationOAuthParamByDefinitionIdOptional(null, requestBody.getDestinationDefinitionId())
        .orElseGet(() -> new DestinationOAuthParameter().withOauthParameterId(UUID.randomUUID()))
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withDestinationDefinitionId(requestBody.getDestinationDefinitionId());
    // TODO validate requestBody.getParams() against
    // spec.getAdvancedAuth().getOauthConfigSpecification().getCompleteOauthServerInputSpecification()
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

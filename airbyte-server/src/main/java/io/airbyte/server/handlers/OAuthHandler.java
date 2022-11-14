/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Iterables;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.generated.CompleteSourceOauthRequest;
import io.airbyte.api.model.generated.DestinationOauthConsentRequest;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.generated.SourceOauthConsentRequest;
import io.airbyte.commons.constants.AirbyteSecretConstants;
import io.airbyte.commons.json.JsonPaths;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.tracker.TrackingMetadata;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OAuthHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(OAuthHandler.class);
  private static final String ERROR_MESSAGE = "failed while reporting usage.";

  private final ConfigRepository configRepository;
  private final OAuthImplementationFactory oAuthImplementationFactory;
  private final TrackingClient trackingClient;
  private final SecretsRepositoryReader secretsRepositoryReader;

  public OAuthHandler(final ConfigRepository configRepository,
                      final HttpClient httpClient,
                      final TrackingClient trackingClient,
                      final SecretsRepositoryReader secretsRepositoryReader) {
    this.configRepository = configRepository;
    this.oAuthImplementationFactory = new OAuthImplementationFactory(configRepository, httpClient);
    this.trackingClient = trackingClient;
    this.secretsRepositoryReader = secretsRepositoryReader;
  }

  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(sourceDefinition);
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    final Map<String, Object> metadata = generateSourceMetadata(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      JsonNode oAuthInputConfigurationForConsent;

      if (sourceDefinitionIdRequestBody.getSourceId() == null) {
        oAuthInputConfigurationForConsent = sourceDefinitionIdRequestBody.getoAuthInputConfiguration();
      } else {
        final SourceConnection hydratedSourceConnection =
            secretsRepositoryReader.getSourceConnectionWithSecrets(sourceDefinitionIdRequestBody.getSourceId());

        List<String> fieldsToGet =
            buildJsonPathFromOAuthFlowInitParameters(spec.getAuthSpecification().getOauth2Specification().getOauthFlowInitParameters());

        JsonNode oAuthInputConfigurationFromDB = getOAuthInputConfiguration(hydratedSourceConnection.getConfiguration(), fieldsToGet);

        oAuthInputConfigurationForConsent = getOauthFromDBIfNeeded(oAuthInputConfigurationFromDB,
            sourceDefinitionIdRequestBody.getoAuthInputConfiguration());
      }

      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
          sourceDefinitionIdRequestBody.getWorkspaceId(),
          sourceDefinitionIdRequestBody.getSourceDefinitionId(),
          sourceDefinitionIdRequestBody.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
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
    final Map<String, Object> metadata = generateDestinationMetadata(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      JsonNode oAuthInputConfigurationForConsent;

      if (destinationDefinitionIdRequestBody.getDestinationId() == null) {
        oAuthInputConfigurationForConsent = destinationDefinitionIdRequestBody.getoAuthInputConfiguration();
      } else {
        final SourceConnection hydratedSourceConnection =
            secretsRepositoryReader.getSourceConnectionWithSecrets(destinationDefinitionIdRequestBody.getDestinationId());

        List<String> fieldsToGet =
            buildJsonPathFromOAuthFlowInitParameters(spec.getAuthSpecification().getOauth2Specification().getOauthFlowInitParameters());

        JsonNode oAuthInputConfigurationFromDB = getOAuthInputConfiguration(hydratedSourceConnection.getConfiguration(), fieldsToGet);

        oAuthInputConfigurationForConsent = getOauthFromDBIfNeeded(oAuthInputConfigurationFromDB,
            destinationDefinitionIdRequestBody.getoAuthInputConfiguration());
      }

      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
          destinationDefinitionIdRequestBody.getWorkspaceId(),
          destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
          destinationDefinitionIdRequestBody.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
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
    final Map<String, Object> metadata = generateSourceMetadata(oauthSourceRequestBody.getSourceDefinitionId());
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
    final Map<String, Object> metadata = generateDestinationMetadata(oauthDestinationRequestBody.getDestinationDefinitionId());
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

  private Map<String, Object> generateSourceMetadata(final UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    return TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
  }

  private Map<String, Object> generateDestinationMetadata(final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    return TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
  }

  @VisibleForTesting
  List<String> buildJsonPathFromOAuthFlowInitParameters(List<List<String>> oAuthFlowInitParameters) {
    return oAuthFlowInitParameters.stream()
        .map(path -> "$." + String.join(".", path))
        .toList();
  }

  @VisibleForTesting
  JsonNode getOauthFromDBIfNeeded(JsonNode oAuthInputConfigurationFromDB, JsonNode oAuthInputConfigurationFromInput) {
    Map<String, String> result = new HashMap<>();

    Jsons.deserializeToStringMap(oAuthInputConfigurationFromInput)
        .forEach((k, v) -> {
          if (AirbyteSecretConstants.SECRETS_MASK.equals(v)) {
            result.put(k, oAuthInputConfigurationFromDB.get(k).textValue());
          } else {
            result.put(k, v);
          }
        });

    return Jsons.jsonNode(result);
  }

  @VisibleForTesting
  JsonNode getOAuthInputConfiguration(JsonNode hydratedSourceConnectionConfiguration, List<String> pathsToGet) {
    return Jsons.jsonNode(pathsToGet.stream().map(path -> Map.entry(path,
        JsonPaths.getSingleValue(hydratedSourceConnectionConfiguration, path)))
        .collect(Collectors.toMap(
            entry -> Iterables.getLast(List.of(entry.getKey().split("\\."))),
            entry -> entry.getValue().get())));
  }

}

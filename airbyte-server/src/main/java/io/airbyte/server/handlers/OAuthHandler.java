/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DESTINATION_DEFINITION_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.SOURCE_DEFINITION_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.WORKSPACE_ID_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
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
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.tracker.TrackingMetadata;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.handlers.helpers.OAuthPathExtractor;
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

  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceOauthConsentRequest)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    ApmTraceUtils.addTagsToTrace(Map.of(WORKSPACE_ID_KEY, sourceOauthConsentRequest.getWorkspaceId(), SOURCE_DEFINITION_ID_KEY,
        sourceOauthConsentRequest.getSourceDefinitionId()));
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(sourceOauthConsentRequest.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(sourceDefinition);
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    final Map<String, Object> metadata = generateSourceMetadata(sourceOauthConsentRequest.getSourceDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      final JsonNode oAuthInputConfigurationForConsent;

      if (sourceOauthConsentRequest.getSourceId() == null) {
        oAuthInputConfigurationForConsent = sourceOauthConsentRequest.getoAuthInputConfiguration();
      } else {
        final SourceConnection hydratedSourceConnection =
            secretsRepositoryReader.getSourceConnectionWithSecrets(sourceOauthConsentRequest.getSourceId());

        oAuthInputConfigurationForConsent = getOAuthInputConfigurationForConsent(spec,
            hydratedSourceConnection.getConfiguration(),
            sourceOauthConsentRequest.getoAuthInputConfiguration());
      }

      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
          sourceOauthConsentRequest.getWorkspaceId(),
          sourceOauthConsentRequest.getSourceDefinitionId(),
          sourceOauthConsentRequest.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
          spec.getAdvancedAuth().getOauthConfigSpecification()));
    } else {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
          sourceOauthConsentRequest.getWorkspaceId(),
          sourceOauthConsentRequest.getSourceDefinitionId(),
          sourceOauthConsentRequest.getRedirectUrl(), Jsons.emptyObject(), null));
    }
    try {
      trackingClient.track(sourceOauthConsentRequest.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    ApmTraceUtils.addTagsToTrace(Map.of(WORKSPACE_ID_KEY, destinationOauthConsentRequest.getWorkspaceId(), DESTINATION_DEFINITION_ID_KEY,
        destinationOauthConsentRequest.getDestinationDefinitionId()));

    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationOauthConsentRequest.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(destinationDefinition);
    final ConnectorSpecification spec = destinationDefinition.getSpec();
    final Map<String, Object> metadata = generateDestinationMetadata(destinationOauthConsentRequest.getDestinationDefinitionId());
    final OAuthConsentRead result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      final JsonNode oAuthInputConfigurationForConsent;

      if (destinationOauthConsentRequest.getDestinationId() == null) {
        oAuthInputConfigurationForConsent = destinationOauthConsentRequest.getoAuthInputConfiguration();
      } else {
        final DestinationConnection hydratedSourceConnection =
            secretsRepositoryReader.getDestinationConnectionWithSecrets(destinationOauthConsentRequest.getDestinationId());

        oAuthInputConfigurationForConsent = getOAuthInputConfigurationForConsent(spec,
            hydratedSourceConnection.getConfiguration(),
            destinationOauthConsentRequest.getoAuthInputConfiguration());

      }

      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
          destinationOauthConsentRequest.getWorkspaceId(),
          destinationOauthConsentRequest.getDestinationDefinitionId(),
          destinationOauthConsentRequest.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
          spec.getAdvancedAuth().getOauthConfigSpecification()));
    } else {
      result = new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
          destinationOauthConsentRequest.getWorkspaceId(),
          destinationOauthConsentRequest.getDestinationDefinitionId(),
          destinationOauthConsentRequest.getRedirectUrl(), Jsons.emptyObject(), null));
    }
    try {
      trackingClient.track(destinationOauthConsentRequest.getWorkspaceId(), "Get Oauth Consent URL - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public Map<String, Object> completeSourceOAuth(final CompleteSourceOauthRequest completeSourceOauthRequest)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    ApmTraceUtils.addTagsToTrace(Map.of(WORKSPACE_ID_KEY, completeSourceOauthRequest.getWorkspaceId(), SOURCE_DEFINITION_ID_KEY,
        completeSourceOauthRequest.getSourceDefinitionId()));

    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(completeSourceOauthRequest.getSourceDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(sourceDefinition);
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    final Map<String, Object> metadata = generateSourceMetadata(completeSourceOauthRequest.getSourceDefinitionId());
    final Map<String, Object> result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      final JsonNode oAuthInputConfigurationForConsent;

      if (completeSourceOauthRequest.getSourceId() == null) {
        oAuthInputConfigurationForConsent = completeSourceOauthRequest.getoAuthInputConfiguration();
      } else {
        final SourceConnection hydratedSourceConnection =
            secretsRepositoryReader.getSourceConnectionWithSecrets(completeSourceOauthRequest.getSourceId());

        oAuthInputConfigurationForConsent = getOAuthInputConfigurationForConsent(spec,
            hydratedSourceConnection.getConfiguration(),
            completeSourceOauthRequest.getoAuthInputConfiguration());
      }

      result = oAuthFlowImplementation.completeSourceOAuth(
          completeSourceOauthRequest.getWorkspaceId(),
          completeSourceOauthRequest.getSourceDefinitionId(),
          completeSourceOauthRequest.getQueryParams(),
          completeSourceOauthRequest.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
          spec.getAdvancedAuth().getOauthConfigSpecification());
    } else {
      // deprecated but this path is kept for connectors that don't define OAuth Spec yet
      result = oAuthFlowImplementation.completeSourceOAuth(
          completeSourceOauthRequest.getWorkspaceId(),
          completeSourceOauthRequest.getSourceDefinitionId(),
          completeSourceOauthRequest.getQueryParams(),
          completeSourceOauthRequest.getRedirectUrl());
    }
    try {
      trackingClient.track(completeSourceOauthRequest.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
    } catch (final Exception e) {
      LOGGER.error(ERROR_MESSAGE, e);
    }
    return result;
  }

  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest completeDestinationOAuthRequest)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    ApmTraceUtils.addTagsToTrace(Map.of(WORKSPACE_ID_KEY, completeDestinationOAuthRequest.getWorkspaceId(), DESTINATION_DEFINITION_ID_KEY,
        completeDestinationOAuthRequest.getDestinationDefinitionId()));

    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(completeDestinationOAuthRequest.getDestinationDefinitionId());
    final OAuthFlowImplementation oAuthFlowImplementation = oAuthImplementationFactory.create(destinationDefinition);
    final ConnectorSpecification spec = destinationDefinition.getSpec();
    final Map<String, Object> metadata = generateDestinationMetadata(completeDestinationOAuthRequest.getDestinationDefinitionId());
    final Map<String, Object> result;
    if (OAuthConfigSupplier.hasOAuthConfigSpecification(spec)) {
      final JsonNode oAuthInputConfigurationForConsent;

      if (completeDestinationOAuthRequest.getDestinationId() == null) {
        oAuthInputConfigurationForConsent = completeDestinationOAuthRequest.getoAuthInputConfiguration();
      } else {
        final DestinationConnection hydratedSourceConnection =
            secretsRepositoryReader.getDestinationConnectionWithSecrets(completeDestinationOAuthRequest.getDestinationId());

        oAuthInputConfigurationForConsent = getOAuthInputConfigurationForConsent(spec,
            hydratedSourceConnection.getConfiguration(),
            completeDestinationOAuthRequest.getoAuthInputConfiguration());

      }

      result = oAuthFlowImplementation.completeDestinationOAuth(
          completeDestinationOAuthRequest.getWorkspaceId(),
          completeDestinationOAuthRequest.getDestinationDefinitionId(),
          completeDestinationOAuthRequest.getQueryParams(),
          completeDestinationOAuthRequest.getRedirectUrl(),
          oAuthInputConfigurationForConsent,
          spec.getAdvancedAuth().getOauthConfigSpecification());
    } else {
      // deprecated but this path is kept for connectors that don't define OAuth Spec yet
      result = oAuthFlowImplementation.completeDestinationOAuth(
          completeDestinationOAuthRequest.getWorkspaceId(),
          completeDestinationOAuthRequest.getDestinationDefinitionId(),
          completeDestinationOAuthRequest.getQueryParams(),
          completeDestinationOAuthRequest.getRedirectUrl());
    }
    try {
      trackingClient.track(completeDestinationOAuthRequest.getWorkspaceId(), "Complete OAuth Flow - Backend", metadata);
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

  private JsonNode getOAuthInputConfigurationForConsent(final ConnectorSpecification spec,
                                                        final JsonNode hydratedSourceConnectionConfiguration,
                                                        final JsonNode oAuthInputConfiguration) {
    final Map<String, String> fieldsToGet =
        buildJsonPathFromOAuthFlowInitParameters(OAuthPathExtractor.extractOauthConfigurationPaths(
            spec.getAdvancedAuth().getOauthConfigSpecification().getOauthUserInputFromConnectorConfigSpecification()));

    final JsonNode oAuthInputConfigurationFromDB = getOAuthInputConfiguration(hydratedSourceConnectionConfiguration, fieldsToGet);

    return getOauthFromDBIfNeeded(oAuthInputConfigurationFromDB,
        oAuthInputConfiguration);
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
  Map<String, String> buildJsonPathFromOAuthFlowInitParameters(final Map<String, List<String>> oAuthFlowInitParameters) {
    return oAuthFlowInitParameters.entrySet().stream()
        .map(entry -> Map.entry(entry.getKey(), "$." + String.join(".", entry.getValue())))
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
  }

  @VisibleForTesting
  JsonNode getOauthFromDBIfNeeded(final JsonNode oAuthInputConfigurationFromDB, final JsonNode oAuthInputConfigurationFromInput) {
    final Map<String, String> result = new HashMap<>();

    Jsons.deserializeToStringMap(oAuthInputConfigurationFromInput)
        .forEach((k, v) -> {
          if (AirbyteSecretConstants.SECRETS_MASK.equals(v)) {
            if (oAuthInputConfigurationFromDB.has(k)) {
              result.put(k, oAuthInputConfigurationFromDB.get(k).textValue());
            } else {
              LOGGER.warn("Missing the key {} in the config store in DB", k);
            }

          } else {
            result.put(k, v);
          }
        });

    return Jsons.jsonNode(result);
  }

  @VisibleForTesting
  JsonNode getOAuthInputConfiguration(final JsonNode hydratedSourceConnectionConfiguration, final Map<String, String> pathsToGet) {
    return Jsons.jsonNode(pathsToGet.entrySet().stream()
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            entry -> JsonPaths.getSingleValue(hydratedSourceConnectionConfiguration, entry.getValue()).get())));
  }

}

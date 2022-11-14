/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.config.persistence.split_secrets.SecretCoordinateToPayload;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpers;
import io.airbyte.config.persistence.split_secrets.SplitSecretConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

/**
 * This class takes secrets as arguments but never returns a secrets as return values (even the ones
 * that are passed in as arguments). It is responsible for writing connector secrets to the correct
 * secrets store and then making sure the remainder of the configuration is written to the Config
 * Database.
 */
@SuppressWarnings({"OptionalUsedAsFieldOrParameterType", "PMD.AvoidThrowingRawExceptionTypes"})
public class SecretsRepositoryWriter {

  private static final UUID NO_WORKSPACE = UUID.fromString("00000000-0000-0000-0000-000000000000");

  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;
  private final Optional<SecretPersistence> longLivedSecretPersistence;
  private final Optional<SecretPersistence> ephemeralSecretPersistence;

  public SecretsRepositoryWriter(final ConfigRepository configRepository,
                                 final Optional<SecretPersistence> longLivedSecretPersistence,
                                 final Optional<SecretPersistence> ephemeralSecretPersistence) {
    this(configRepository, new JsonSchemaValidator(), longLivedSecretPersistence, ephemeralSecretPersistence);
  }

  @VisibleForTesting
  SecretsRepositoryWriter(final ConfigRepository configRepository,
                          final JsonSchemaValidator validator,
                          final Optional<SecretPersistence> longLivedSecretPersistence,
                          final Optional<SecretPersistence> ephemeralSecretPersistence) {
    this.configRepository = configRepository;
    this.validator = validator;
    this.longLivedSecretPersistence = longLivedSecretPersistence;
    this.ephemeralSecretPersistence = ephemeralSecretPersistence;
  }

  private Optional<SourceConnection> getSourceIfExists(final UUID sourceId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getSourceConnection(sourceId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  // validates too!
  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    final var previousSourceConnection = getSourceIfExists(source.getSourceId())
        .map(SourceConnection::getConfiguration);

    // strip secrets
    final JsonNode partialConfig = statefulUpdateSecrets(
        source.getWorkspaceId(),
        previousSourceConnection,
        source.getConfiguration(),
        connectorSpecification.getConnectionSpecification(),
        source.getTombstone() == null || !source.getTombstone());
    final SourceConnection partialSource = Jsons.clone(source).withConfiguration(partialConfig);

    configRepository.writeSourceConnectionNoSecrets(partialSource);
  }

  private Optional<DestinationConnection> getDestinationIfExists(final UUID destinationId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getDestinationConnection(destinationId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeDestinationConnection(final DestinationConnection destination, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    final var previousDestinationConnection = getDestinationIfExists(destination.getDestinationId())
        .map(DestinationConnection::getConfiguration);

    final JsonNode partialConfig = statefulUpdateSecrets(
        destination.getWorkspaceId(),
        previousDestinationConnection,
        destination.getConfiguration(),
        connectorSpecification.getConnectionSpecification(),
        destination.getTombstone() == null || !destination.getTombstone());
    final DestinationConnection partialDestination = Jsons.clone(destination).withConfiguration(partialConfig);

    configRepository.writeDestinationConnectionNoSecrets(partialDestination);
  }

  /**
   * Detects secrets in the configuration. Writes them to the secrets store. It returns the config
   * stripped of secrets (replaced with pointers to the secrets store).
   *
   * @param workspaceId workspace id for the config
   * @param fullConfig full config
   * @param spec connector specification
   * @return partial config
   */
  @SuppressWarnings("unused")
  private JsonNode statefulSplitSecrets(final UUID workspaceId, final JsonNode fullConfig, final ConnectorSpecification spec) {
    return splitSecretConfig(workspaceId, fullConfig, spec, longLivedSecretPersistence);
  }

  // todo (cgardens) - the contract on this method is hard to follow, because it sometimes returns
  // secrets (i.e. when there is no longLivedSecretPersistence). If we treated all secrets the same
  // (i.e. used a separate db for secrets when the user didn't provide a store), this would be easier
  // to reason about.
  /**
   * If a secrets store is present, this method attempts to fetch the existing config and merge its
   * secrets with the passed in config. If there is no secrets store, it just returns the passed in
   * config. Also validates the config.
   *
   * @param workspaceId workspace id for the config
   * @param oldConfig old full config
   * @param fullConfig new full config
   * @param spec connector specification
   * @param validate should the spec be validated, tombstone entries should not be validated
   * @return partial config
   */
  private JsonNode statefulUpdateSecrets(final UUID workspaceId,
                                         final Optional<JsonNode> oldConfig,
                                         final JsonNode fullConfig,
                                         final JsonNode spec,
                                         final boolean validate)
      throws JsonValidationException {
    if (validate) {
      validator.ensure(spec, fullConfig);
    }

    if (longLivedSecretPersistence.isEmpty()) {
      return fullConfig;
    }

    final SplitSecretConfig splitSecretConfig;
    if (oldConfig.isPresent()) {
      splitSecretConfig = SecretsHelpers.splitAndUpdateConfig(
          workspaceId,
          oldConfig.get(),
          fullConfig,
          spec,
          longLivedSecretPersistence.get());
    } else {
      splitSecretConfig = SecretsHelpers.splitConfig(
          workspaceId,
          fullConfig,
          spec);
    }
    splitSecretConfig.getCoordinateToPayload().forEach(longLivedSecretPersistence.get()::write);
    return splitSecretConfig.getPartialConfig();
  }

  /**
   * @param fullConfig full config
   * @param spec connector specification
   * @return partial config
   */
  public JsonNode statefulSplitEphemeralSecrets(final JsonNode fullConfig, final ConnectorSpecification spec) {
    return splitSecretConfig(NO_WORKSPACE, fullConfig, spec, ephemeralSecretPersistence);
  }

  private JsonNode splitSecretConfig(final UUID workspaceId,
                                     final JsonNode fullConfig,
                                     final ConnectorSpecification spec,
                                     final Optional<SecretPersistence> secretPersistence) {
    if (secretPersistence.isPresent()) {
      final SplitSecretConfig splitSecretConfig = SecretsHelpers.splitConfig(workspaceId, fullConfig, spec.getConnectionSpecification());
      splitSecretConfig.getCoordinateToPayload().forEach(secretPersistence.get()::write);
      return splitSecretConfig.getPartialConfig();
    } else {
      return fullConfig;
    }
  }

  public void writeServiceAccountJsonCredentials(final WorkspaceServiceAccount workspaceServiceAccount)
      throws JsonValidationException, IOException {
    final WorkspaceServiceAccount workspaceServiceAccountForDB = getWorkspaceServiceAccountWithSecretCoordinate(workspaceServiceAccount);
    configRepository.writeWorkspaceServiceAccountNoSecrets(workspaceServiceAccountForDB);
  }

  /**
   * This method is to encrypt the secret JSON key and HMAC key of a GCP service account a associated
   * with a workspace. If in future we build a similar feature i.e. an AWS account associated with a
   * workspace, we will have to build new implementation for it
   */
  private WorkspaceServiceAccount getWorkspaceServiceAccountWithSecretCoordinate(final WorkspaceServiceAccount workspaceServiceAccount)
      throws JsonValidationException, IOException {
    if (longLivedSecretPersistence.isPresent()) {
      final WorkspaceServiceAccount clonedWorkspaceServiceAccount = Jsons.clone(workspaceServiceAccount);
      final Optional<WorkspaceServiceAccount> optionalWorkspaceServiceAccount = getOptionalWorkspaceServiceAccount(
          workspaceServiceAccount.getWorkspaceId());
      // Convert the JSON key of Service Account into secret co-oridnate. Ref :
      // https://cloud.google.com/iam/docs/service-accounts#key-types
      if (workspaceServiceAccount.getJsonCredential() != null) {
        final SecretCoordinateToPayload jsonCredSecretCoordinateToPayload =
            SecretsHelpers.convertServiceAccountCredsToSecret(workspaceServiceAccount.getJsonCredential().toPrettyString(),
                longLivedSecretPersistence.get(),
                workspaceServiceAccount.getWorkspaceId(),
                UUID::randomUUID,
                optionalWorkspaceServiceAccount.map(WorkspaceServiceAccount::getJsonCredential).orElse(null),
                "json");
        longLivedSecretPersistence.get().write(jsonCredSecretCoordinateToPayload.secretCoordinate(), jsonCredSecretCoordinateToPayload.payload());
        clonedWorkspaceServiceAccount.setJsonCredential(jsonCredSecretCoordinateToPayload.secretCoordinateForDB());
      }
      // Convert the HMAC key of Service Account into secret co-oridnate. Ref :
      // https://cloud.google.com/storage/docs/authentication/hmackeys
      if (workspaceServiceAccount.getHmacKey() != null) {
        final SecretCoordinateToPayload hmackKeySecretCoordinateToPayload =
            SecretsHelpers.convertServiceAccountCredsToSecret(workspaceServiceAccount.getHmacKey().toString(),
                longLivedSecretPersistence.get(),
                workspaceServiceAccount.getWorkspaceId(),
                UUID::randomUUID,
                optionalWorkspaceServiceAccount.map(WorkspaceServiceAccount::getHmacKey).orElse(null),
                "hmac");
        longLivedSecretPersistence.get().write(hmackKeySecretCoordinateToPayload.secretCoordinate(), hmackKeySecretCoordinateToPayload.payload());
        clonedWorkspaceServiceAccount.setHmacKey(hmackKeySecretCoordinateToPayload.secretCoordinateForDB());
      }
      return clonedWorkspaceServiceAccount;
    }
    return workspaceServiceAccount;
  }

  public Optional<WorkspaceServiceAccount> getOptionalWorkspaceServiceAccount(final UUID workspaceId)
      throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getWorkspaceServiceAccountNoSecrets(workspaceId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeWorkspace(final StandardWorkspace workspace)
      throws JsonValidationException, IOException {
    // Get the schema for the webhook config so we can split out any secret fields.
    final JsonNode webhookConfigSchema = Jsons.jsonNodeFromFile(ConfigSchema.WORKSPACE_WEBHOOK_OPERATION_CONFIGS.getConfigSchemaFile());
    // Check if there's an existing config, so we can re-use the secret coordinates.
    final var previousWorkspace = getWorkspaceIfExists(workspace.getWorkspaceId(), false);
    Optional<JsonNode> previousWebhookConfigs = Optional.empty();
    if (previousWorkspace.isPresent() && previousWorkspace.get().getWebhookOperationConfigs() != null) {
      previousWebhookConfigs = Optional.of(previousWorkspace.get().getWebhookOperationConfigs());
    }
    // Split out the secrets from the webhook config.
    final JsonNode partialConfig = workspace.getWebhookOperationConfigs() == null ? null
        : statefulUpdateSecrets(
            workspace.getWorkspaceId(),
            previousWebhookConfigs,
            workspace.getWebhookOperationConfigs(),
            webhookConfigSchema, true);
    final StandardWorkspace partialWorkspace = Jsons.clone(workspace);
    if (partialConfig != null) {
      partialWorkspace.withWebhookOperationConfigs(partialConfig);
    }
    configRepository.writeStandardWorkspaceNoSecrets(partialWorkspace);
  }

  private Optional<StandardWorkspace> getWorkspaceIfExists(final UUID workspaceId, final boolean includeTombstone) {
    try {
      final StandardWorkspace existingWorkspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, includeTombstone);
      return existingWorkspace == null ? Optional.empty() : Optional.of(existingWorkspace);
    } catch (final JsonValidationException | IOException | ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

}

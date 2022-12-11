/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This class is responsible for fetching both connectors and their secrets (from separate secrets
 * stores). All methods in this class return secrets! Use it carefully.
 */
public class SecretsRepositoryReader {

  private final ConfigRepository configRepository;
  private final SecretsHydrator secretsHydrator;

  public SecretsRepositoryReader(final ConfigRepository configRepository,
                                 final SecretsHydrator secretsHydrator) {
    this.configRepository = configRepository;
    this.secretsHydrator = secretsHydrator;
  }

  public SourceConnection getSourceConnectionWithSecrets(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final var source = configRepository.getSourceConnection(sourceId);
    return hydrateSourcePartialConfig(source);
  }

  public List<SourceConnection> listSourceConnectionWithSecrets() throws JsonValidationException, IOException {
    final var sources = configRepository.listSourceConnection();

    return sources
        .stream()
        .map(partialSource -> Exceptions.toRuntime(() -> hydrateSourcePartialConfig(partialSource)))
        .collect(Collectors.toList());
  }

  public DestinationConnection getDestinationConnectionWithSecrets(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final var destination = configRepository.getDestinationConnection(destinationId);
    return hydrateDestinationPartialConfig(destination);
  }

  public List<DestinationConnection> listDestinationConnectionWithSecrets() throws JsonValidationException, IOException {
    final var destinations = configRepository.listDestinationConnection();

    return destinations
        .stream()
        .map(partialDestination -> Exceptions.toRuntime(() -> hydrateDestinationPartialConfig(partialDestination)))
        .collect(Collectors.toList());
  }

  private SourceConnection hydrateSourcePartialConfig(final SourceConnection sourceWithPartialConfig) {
    final JsonNode hydratedConfig = secretsHydrator.hydrate(sourceWithPartialConfig.getConfiguration());
    return Jsons.clone(sourceWithPartialConfig).withConfiguration(hydratedConfig);
  }

  private DestinationConnection hydrateDestinationPartialConfig(final DestinationConnection sourceWithPartialConfig) {
    final JsonNode hydratedConfig = secretsHydrator.hydrate(sourceWithPartialConfig.getConfiguration());
    return Jsons.clone(sourceWithPartialConfig).withConfiguration(hydratedConfig);
  }

  @SuppressWarnings("unused")
  private void hydrateValuesIfKeyPresent(final String key, final Map<String, Stream<JsonNode>> dump) {
    if (dump.containsKey(key)) {
      final Stream<JsonNode> augmentedValue = dump.get(key).map(secretsHydrator::hydrate);
      dump.put(key, augmentedValue);
    }
  }

  public WorkspaceServiceAccount getWorkspaceServiceAccountWithSecrets(final UUID workspaceId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final WorkspaceServiceAccount workspaceServiceAccount = configRepository.getWorkspaceServiceAccountNoSecrets(workspaceId);

    final JsonNode jsonCredential =
        workspaceServiceAccount.getJsonCredential() != null ? secretsHydrator.hydrateSecretCoordinate(workspaceServiceAccount.getJsonCredential())
            : null;

    final JsonNode hmacKey =
        workspaceServiceAccount.getHmacKey() != null ? secretsHydrator.hydrateSecretCoordinate(workspaceServiceAccount.getHmacKey()) : null;

    return Jsons.clone(workspaceServiceAccount).withJsonCredential(jsonCredential).withHmacKey(hmacKey);
  }

  public StandardWorkspace getWorkspaceWithSecrets(final UUID workspaceId, final boolean includeTombstone)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, includeTombstone);
    final JsonNode webhookConfigs = secretsHydrator.hydrate(workspace.getWebhookOperationConfigs());
    workspace.withWebhookOperationConfigs(webhookConfigs);
    return workspace;
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.commons.json.JsonSchemas;
import java.io.File;
import java.nio.file.Path;
import java.util.function.Function;

@SuppressWarnings({"PMD.AvoidThrowingRawExceptionTypes", "PMD.NullAssignment"})
public enum ConfigSchema implements AirbyteConfig {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.yaml",
      StandardWorkspace.class,
      standardWorkspace -> standardWorkspace.getWorkspaceId().toString(),
      "workspaceId"),

  WORKSPACE_SERVICE_ACCOUNT("WorkspaceServiceAccount.yaml",
      WorkspaceServiceAccount.class,
      workspaceServiceAccount -> workspaceServiceAccount.getWorkspaceId().toString(),
      "workspaceId"),

  WORKSPACE_WEBHOOK_OPERATION_CONFIGS("WebhookOperationConfigs.yaml",
      WebhookOperationConfigs.class),

  // source
  STANDARD_SOURCE_DEFINITION("StandardSourceDefinition.yaml",
      StandardSourceDefinition.class,
      standardSourceDefinition -> standardSourceDefinition.getSourceDefinitionId().toString(),
      "sourceDefinitionId"),
  SOURCE_CONNECTION("SourceConnection.yaml",
      SourceConnection.class,
      sourceConnection -> sourceConnection.getSourceId().toString(),
      "sourceId"),

  // destination
  STANDARD_DESTINATION_DEFINITION("StandardDestinationDefinition.yaml",
      StandardDestinationDefinition.class,
      standardDestinationDefinition -> standardDestinationDefinition.getDestinationDefinitionId().toString(),
      "destinationDefinitionId"),
  DESTINATION_CONNECTION("DestinationConnection.yaml",
      DestinationConnection.class,
      destinationConnection -> destinationConnection.getDestinationId().toString(),
      "destinationId"),

  // sync (i.e. connection)
  STANDARD_SYNC("StandardSync.yaml",
      StandardSync.class,
      standardSync -> standardSync.getConnectionId().toString(),
      "connectionId"),
  STANDARD_SYNC_OPERATION("StandardSyncOperation.yaml",
      StandardSyncOperation.class,
      standardSyncOperation -> standardSyncOperation.getOperationId().toString(),
      "operationId"),
  STANDARD_SYNC_STATE("StandardSyncState.yaml",
      StandardSyncState.class,
      standardSyncState -> standardSyncState.getConnectionId().toString(),
      "connectionId"),

  SOURCE_OAUTH_PARAM("SourceOAuthParameter.yaml", SourceOAuthParameter.class,
      sourceOAuthParameter -> sourceOAuthParameter.getOauthParameterId().toString(),
      "oauthParameterId"),
  DESTINATION_OAUTH_PARAM("DestinationOAuthParameter.yaml", DestinationOAuthParameter.class,
      destinationOAuthParameter -> destinationOAuthParameter.getOauthParameterId().toString(),
      "oauthParameterId"),

  STANDARD_SYNC_SUMMARY("StandardSyncSummary.yaml", StandardSyncSummary.class),

  ACTOR_CATALOG("ActorCatalog.yaml", ActorCatalog.class),
  ACTOR_CATALOG_FETCH_EVENT("ActorCatalogFetchEvent.yaml", ActorCatalogFetchEvent.class),

  // worker
  STANDARD_SYNC_INPUT("StandardSyncInput.yaml", StandardSyncInput.class),
  NORMALIZATION_INPUT("NormalizationInput.yaml", NormalizationInput.class),
  OPERATOR_DBT_INPUT("OperatorDbtInput.yaml", OperatorDbtInput.class),
  STANDARD_SYNC_OUTPUT("StandardSyncOutput.yaml", StandardSyncOutput.class),
  REPLICATION_OUTPUT("ReplicationOutput.yaml", ReplicationOutput.class),
  STATE("State.yaml", State.class);

  static final Path KNOWN_SCHEMAS_ROOT = JsonSchemas.prepareSchemas("types", ConfigSchema.class);

  private final String schemaFilename;
  private final Class<?> className;
  private final Function<?, String> extractId;
  private final String idFieldName;

  <T> ConfigSchema(final String schemaFilename,
                   final Class<T> className,
                   final Function<T, String> extractId,
                   final String idFieldName) {
    this.schemaFilename = schemaFilename;
    this.className = className;
    this.extractId = extractId;
    this.idFieldName = idFieldName;
  }

  <T> ConfigSchema(final String schemaFilename,
                   final Class<T> className) {
    this.schemaFilename = schemaFilename;
    this.className = className;
    this.extractId = object -> {
      throw new RuntimeException(className.getSimpleName() + " doesn't have an id");
    };
    this.idFieldName = null;
  }

  @Override
  public File getConfigSchemaFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

  @Override
  public <T> Class<T> getClassName() {
    return (Class<T>) className;
  }

  @Override
  public <T> String getId(final T object) {
    if (getClassName().isInstance(object)) {
      return ((Function<T, String>) extractId).apply(object);
    }
    throw new RuntimeException("Object: " + object + " is not instance of class " + getClassName().getName());
  }

  @Override
  public String getIdFieldName() {
    return idFieldName;
  }

}

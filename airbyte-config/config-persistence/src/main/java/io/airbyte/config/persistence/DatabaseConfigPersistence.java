/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_OAUTH_PARAMETER;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION_OPERATION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.OPERATION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.STATE;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE_SERVICE_ACCOUNT;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.select;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.configs.jooq.generated.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Record1;
import org.jooq.Result;
import org.jooq.SelectJoinStep;
import org.jooq.TableField;
import org.jooq.impl.TableImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings({"PMD.CyclomaticComplexity", "PMD.CognitiveComplexity", "PMD.NPathComplexity", "PMD.ExcessiveMethodLength",
  "PMD.AvoidThrowingRawExceptionTypes", "PMD.ShortVariable", "PMD.LongVariable", "PMD.ExcessiveClassLength", "PMD.AvoidLiteralsInIfCondition"})
public class DatabaseConfigPersistence implements ConfigPersistence {

  private final ExceptionWrappingDatabase database;
  private final JsonSecretsProcessor jsonSecretsProcessor;
  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseConfigPersistence.class);
  private static final String UNKNOWN_CONFIG_TYPE = "Unknown Config Type ";
  private static final String NOT_FOUND = " not found";

  /**
   * Entrypoint into DatabaseConfigPersistence. Except in testing, we should never be using it without
   * it being decorated with validation classes.
   *
   * @param database - database where configs are stored
   * @param jsonSecretsProcessor - for filtering secrets in export
   * @return database config persistence wrapped in validation decorators
   */
  public static ConfigPersistence createWithValidation(final Database database,
                                                       final JsonSecretsProcessor jsonSecretsProcessor) {
    return new ValidatingConfigPersistence(new DatabaseConfigPersistence(database, jsonSecretsProcessor));
  }

  public DatabaseConfigPersistence(final Database database, final JsonSecretsProcessor jsonSecretsProcessor) {
    this.database = new ExceptionWrappingDatabase(database);
    this.jsonSecretsProcessor = jsonSecretsProcessor;
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      return (T) getStandardWorkspace(configId);
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      return (T) getStandardSourceDefinition(configId);
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      return (T) getStandardDestinationDefinition(configId);
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      return (T) getSourceConnection(configId);
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      return (T) getDestinationConnection(configId);
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      return (T) getSourceOauthParam(configId);
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      return (T) getDestinationOauthParam(configId);
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      return (T) getStandardSyncOperation(configId);
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      return (T) getStandardSync(configId);
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      return (T) getStandardSyncState(configId);
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      return (T) getActorCatalog(configId);
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      return (T) getActorCatalogFetchEvent(configId);
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      return (T) getWorkspaceServiceAccount(configId);
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  private StandardWorkspace getStandardWorkspace(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardWorkspace>> result = listStandardWorkspaceWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_WORKSPACE);
    return result.get(0).getConfig();
  }

  private WorkspaceServiceAccount getWorkspaceServiceAccount(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<WorkspaceServiceAccount>> result = listWorkspaceServiceAccountWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.WORKSPACE_SERVICE_ACCOUNT);
    return result.get(0).getConfig();
  }

  private StandardSourceDefinition getStandardSourceDefinition(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardSourceDefinition>> result =
        listStandardSourceDefinitionWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_SOURCE_DEFINITION);
    return result.get(0).getConfig();
  }

  private StandardDestinationDefinition getStandardDestinationDefinition(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardDestinationDefinition>> result =
        listStandardDestinationDefinitionWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_DESTINATION_DEFINITION);
    return result.get(0).getConfig();
  }

  private SourceConnection getSourceConnection(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<SourceConnection>> result = listSourceConnectionWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.SOURCE_CONNECTION);
    return result.get(0).getConfig();
  }

  private DestinationConnection getDestinationConnection(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<DestinationConnection>> result = listDestinationConnectionWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.DESTINATION_CONNECTION);
    return result.get(0).getConfig();
  }

  private SourceOAuthParameter getSourceOauthParam(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<SourceOAuthParameter>> result = listSourceOauthParamWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.SOURCE_OAUTH_PARAM);
    return result.get(0).getConfig();
  }

  private DestinationOAuthParameter getDestinationOauthParam(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<DestinationOAuthParameter>> result = listDestinationOauthParamWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.DESTINATION_OAUTH_PARAM);
    return result.get(0).getConfig();
  }

  private StandardSyncOperation getStandardSyncOperation(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardSyncOperation>> result = listStandardSyncOperationWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_SYNC_OPERATION);
    return result.get(0).getConfig();
  }

  private StandardSync getStandardSync(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardSync>> result = listStandardSyncWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_SYNC);
    return result.get(0).getConfig();
  }

  private StandardSyncState getStandardSyncState(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardSyncState>> result = listStandardSyncStateWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.STANDARD_SYNC_STATE);
    return result.get(0).getConfig();
  }

  private ActorCatalog getActorCatalog(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<ActorCatalog>> result = listActorCatalogWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.ACTOR_CATALOG);
    return result.get(0).getConfig();
  }

  private ActorCatalogFetchEvent getActorCatalogFetchEvent(final String configId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<ActorCatalogFetchEvent>> result = listActorCatalogFetchEventWithMetadata(Optional.of(UUID.fromString(configId)));
    validate(configId, result, ConfigSchema.ACTOR_CATALOG_FETCH_EVENT);
    return result.get(0).getConfig();
  }

  private List<UUID> connectionOperationIds(final UUID connectionId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(CONNECTION_OPERATION)
        .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
        .fetch());

    final List<UUID> ids = new ArrayList<>();
    for (final Record record : result) {
      ids.add(record.get(CONNECTION_OPERATION.OPERATION_ID));
    }

    return ids;
  }

  private <T> void validate(final String configId, final List<ConfigWithMetadata<T>> result, final AirbyteConfig airbyteConfig)
      throws ConfigNotFoundException {
    if (result.isEmpty()) {
      throw new ConfigNotFoundException(airbyteConfig, configId);
    } else if (result.size() > 1) {
      throw new IllegalStateException(String.format("Multiple %s configs found for ID %s: %s", airbyteConfig, configId, result));
    }
  }

  private <T> ConfigWithMetadata<T> validateAndReturn(final String configId,
                                                      final List<ConfigWithMetadata<T>> result,
                                                      final AirbyteConfig airbyteConfig)
      throws ConfigNotFoundException {
    validate(configId, result, airbyteConfig);
    return result.get(0);
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) throws JsonValidationException, IOException {
    final List<T> config = new ArrayList<>();
    listConfigsWithMetadata(configType, clazz).forEach(c -> config.add(c.getConfig()));
    return config;
  }

  @Override
  public <T> ConfigWithMetadata<T> getConfigWithMetadata(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Optional<UUID> configIdOpt = Optional.of(UUID.fromString(configId));
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardWorkspaceWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardSourceDefinitionWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardDestinationDefinitionWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listSourceConnectionWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listDestinationConnectionWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listSourceOauthParamWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listDestinationOauthParamWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardSyncOperationWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardSyncWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listStandardSyncStateWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listActorCatalogWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listActorCatalogFetchEventWithMetadata(configIdOpt), configType);
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      return (ConfigWithMetadata<T>) validateAndReturn(configId, listWorkspaceServiceAccountWithMetadata(configIdOpt), configType);
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz) throws IOException {
    final List<ConfigWithMetadata<T>> configWithMetadata = new ArrayList<>();
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      listStandardWorkspaceWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      listStandardSourceDefinitionWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      listStandardDestinationDefinitionWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      listSourceConnectionWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      listDestinationConnectionWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      listSourceOauthParamWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      listDestinationOauthParamWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      listStandardSyncOperationWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      listStandardSyncWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      listStandardSyncStateWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      listActorCatalogWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      listActorCatalogFetchEventWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      listWorkspaceServiceAccountWithMetadata().forEach(c -> configWithMetadata.add((ConfigWithMetadata<T>) c));
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }

    return configWithMetadata;
  }

  private List<ConfigWithMetadata<StandardWorkspace>> listStandardWorkspaceWithMetadata() throws IOException {
    return listStandardWorkspaceWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardWorkspace>> listStandardWorkspaceWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(WORKSPACE);
      if (configId.isPresent()) {
        return query.where(WORKSPACE.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    final List<ConfigWithMetadata<StandardWorkspace>> standardWorkspaces = new ArrayList<>();
    for (final Record record : result) {
      final StandardWorkspace workspace = DbConverter.buildStandardWorkspace(record);
      standardWorkspaces.add(new ConfigWithMetadata<>(
          record.get(WORKSPACE.ID).toString(),
          ConfigSchema.STANDARD_WORKSPACE.name(),
          record.get(WORKSPACE.CREATED_AT).toInstant(),
          record.get(WORKSPACE.UPDATED_AT).toInstant(),
          workspace));
    }
    return standardWorkspaces;
  }

  private List<ConfigWithMetadata<WorkspaceServiceAccount>> listWorkspaceServiceAccountWithMetadata() throws IOException {
    return listWorkspaceServiceAccountWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<WorkspaceServiceAccount>> listWorkspaceServiceAccountWithMetadata(final Optional<UUID> configId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(WORKSPACE_SERVICE_ACCOUNT);
      if (configId.isPresent()) {
        return query.where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    final List<ConfigWithMetadata<WorkspaceServiceAccount>> workspaceServiceAccounts = new ArrayList<>();
    for (final Record record : result) {
      final WorkspaceServiceAccount workspaceServiceAccount = DbConverter.buildWorkspaceServiceAccount(record);
      workspaceServiceAccounts.add(new ConfigWithMetadata<>(
          record.get(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID).toString(),
          ConfigSchema.WORKSPACE_SERVICE_ACCOUNT.name(),
          record.get(WORKSPACE_SERVICE_ACCOUNT.CREATED_AT).toInstant(),
          record.get(WORKSPACE_SERVICE_ACCOUNT.UPDATED_AT).toInstant(),
          workspaceServiceAccount));
    }
    return workspaceServiceAccounts;
  }

  private List<ConfigWithMetadata<StandardSourceDefinition>> listStandardSourceDefinitionWithMetadata() throws IOException {
    return listStandardSourceDefinitionWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardSourceDefinition>> listStandardSourceDefinitionWithMetadata(final Optional<UUID> configId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_DEFINITION);
      if (configId.isPresent()) {
        return query.where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.source), ACTOR_DEFINITION.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.source)).fetch();
    });

    final List<ConfigWithMetadata<StandardSourceDefinition>> standardSourceDefinitions = new ArrayList<>();

    for (final Record record : result) {
      final StandardSourceDefinition standardSourceDefinition = DbConverter.buildStandardSourceDefinition(record);
      standardSourceDefinitions.add(new ConfigWithMetadata<>(
          record.get(ACTOR_DEFINITION.ID).toString(),
          ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
          record.get(ACTOR_DEFINITION.CREATED_AT).toInstant(),
          record.get(ACTOR_DEFINITION.UPDATED_AT).toInstant(),
          standardSourceDefinition));
    }
    return standardSourceDefinitions;
  }

  private List<ConfigWithMetadata<StandardDestinationDefinition>> listStandardDestinationDefinitionWithMetadata() throws IOException {
    return listStandardDestinationDefinitionWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardDestinationDefinition>> listStandardDestinationDefinitionWithMetadata(final Optional<UUID> configId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_DEFINITION);
      if (configId.isPresent()) {
        return query.where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.destination), ACTOR_DEFINITION.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.destination)).fetch();
    });

    final List<ConfigWithMetadata<StandardDestinationDefinition>> standardDestinationDefinitions = new ArrayList<>();

    for (final Record record : result) {
      final StandardDestinationDefinition standardDestinationDefinition = DbConverter.buildStandardDestinationDefinition(record);
      standardDestinationDefinitions.add(new ConfigWithMetadata<>(
          record.get(ACTOR_DEFINITION.ID).toString(),
          ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(),
          record.get(ACTOR_DEFINITION.CREATED_AT).toInstant(),
          record.get(ACTOR_DEFINITION.UPDATED_AT).toInstant(),
          standardDestinationDefinition));
    }
    return standardDestinationDefinitions;
  }

  private List<ConfigWithMetadata<SourceConnection>> listSourceConnectionWithMetadata() throws IOException {
    return listSourceConnectionWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<SourceConnection>> listSourceConnectionWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR);
      if (configId.isPresent()) {
        return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.source), ACTOR.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.source)).fetch();
    });

    final List<ConfigWithMetadata<SourceConnection>> sourceConnections = new ArrayList<>();
    for (final Record record : result) {
      final SourceConnection sourceConnection = buildSourceConnection(record);
      sourceConnections.add(new ConfigWithMetadata<>(
          record.get(ACTOR.ID).toString(),
          ConfigSchema.SOURCE_CONNECTION.name(),
          record.get(ACTOR.CREATED_AT).toInstant(),
          record.get(ACTOR.UPDATED_AT).toInstant(),
          sourceConnection));
    }
    return sourceConnections;
  }

  private SourceConnection buildSourceConnection(final Record record) {
    return new SourceConnection()
        .withSourceId(record.get(ACTOR.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR.WORKSPACE_ID))
        .withSourceDefinitionId(record.get(ACTOR.ACTOR_DEFINITION_ID))
        .withTombstone(record.get(ACTOR.TOMBSTONE))
        .withName(record.get(ACTOR.NAME));
  }

  private List<ConfigWithMetadata<DestinationConnection>> listDestinationConnectionWithMetadata() throws IOException {
    return listDestinationConnectionWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<DestinationConnection>> listDestinationConnectionWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR);
      if (configId.isPresent()) {
        return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.destination), ACTOR.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.destination)).fetch();
    });

    final List<ConfigWithMetadata<DestinationConnection>> destinationConnections = new ArrayList<>();
    for (final Record record : result) {
      final DestinationConnection destinationConnection = buildDestinationConnection(record);
      destinationConnections.add(new ConfigWithMetadata<>(
          record.get(ACTOR.ID).toString(),
          ConfigSchema.DESTINATION_CONNECTION.name(),
          record.get(ACTOR.CREATED_AT).toInstant(),
          record.get(ACTOR.UPDATED_AT).toInstant(),
          destinationConnection));
    }
    return destinationConnections;
  }

  private DestinationConnection buildDestinationConnection(final Record record) {
    return new DestinationConnection()
        .withDestinationId(record.get(ACTOR.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR.WORKSPACE_ID))
        .withDestinationDefinitionId(record.get(ACTOR.ACTOR_DEFINITION_ID))
        .withTombstone(record.get(ACTOR.TOMBSTONE))
        .withName(record.get(ACTOR.NAME));
  }

  private List<ConfigWithMetadata<SourceOAuthParameter>> listSourceOauthParamWithMetadata() throws IOException {
    return listSourceOauthParamWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<SourceOAuthParameter>> listSourceOauthParamWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      if (configId.isPresent()) {
        return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.source), ACTOR_OAUTH_PARAMETER.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.source)).fetch();
    });

    final List<ConfigWithMetadata<SourceOAuthParameter>> sourceOAuthParameters = new ArrayList<>();
    for (final Record record : result) {
      final SourceOAuthParameter sourceOAuthParameter = DbConverter.buildSourceOAuthParameter(record);
      sourceOAuthParameters.add(new ConfigWithMetadata<>(
          record.get(ACTOR_OAUTH_PARAMETER.ID).toString(),
          ConfigSchema.SOURCE_OAUTH_PARAM.name(),
          record.get(ACTOR_OAUTH_PARAMETER.CREATED_AT).toInstant(),
          record.get(ACTOR_OAUTH_PARAMETER.UPDATED_AT).toInstant(),
          sourceOAuthParameter));
    }
    return sourceOAuthParameters;
  }

  private List<ConfigWithMetadata<DestinationOAuthParameter>> listDestinationOauthParamWithMetadata() throws IOException {
    return listDestinationOauthParamWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<DestinationOAuthParameter>> listDestinationOauthParamWithMetadata(final Optional<UUID> configId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      if (configId.isPresent()) {
        return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.destination), ACTOR_OAUTH_PARAMETER.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.destination)).fetch();
    });

    final List<ConfigWithMetadata<DestinationOAuthParameter>> destinationOAuthParameters = new ArrayList<>();
    for (final Record record : result) {
      final DestinationOAuthParameter destinationOAuthParameter = DbConverter.buildDestinationOAuthParameter(record);
      destinationOAuthParameters.add(new ConfigWithMetadata<>(
          record.get(ACTOR_OAUTH_PARAMETER.ID).toString(),
          ConfigSchema.DESTINATION_OAUTH_PARAM.name(),
          record.get(ACTOR_OAUTH_PARAMETER.CREATED_AT).toInstant(),
          record.get(ACTOR_OAUTH_PARAMETER.UPDATED_AT).toInstant(),
          destinationOAuthParameter));
    }
    return destinationOAuthParameters;
  }

  private List<ConfigWithMetadata<StandardSyncOperation>> listStandardSyncOperationWithMetadata() throws IOException {
    return listStandardSyncOperationWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardSyncOperation>> listStandardSyncOperationWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(OPERATION);
      if (configId.isPresent()) {
        return query.where(OPERATION.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    final List<ConfigWithMetadata<StandardSyncOperation>> standardSyncOperations = new ArrayList<>();
    for (final Record record : result) {
      final StandardSyncOperation standardSyncOperation = buildStandardSyncOperation(record);
      standardSyncOperations.add(new ConfigWithMetadata<>(
          record.get(OPERATION.ID).toString(),
          ConfigSchema.STANDARD_SYNC_OPERATION.name(),
          record.get(OPERATION.CREATED_AT).toInstant(),
          record.get(OPERATION.UPDATED_AT).toInstant(),
          standardSyncOperation));
    }
    return standardSyncOperations;
  }

  private StandardSyncOperation buildStandardSyncOperation(final Record record) {
    return new StandardSyncOperation()
        .withOperationId(record.get(OPERATION.ID))
        .withName(record.get(OPERATION.NAME))
        .withWorkspaceId(record.get(OPERATION.WORKSPACE_ID))
        .withOperatorType(Enums.toEnum(record.get(OPERATION.OPERATOR_TYPE, String.class), OperatorType.class).orElseThrow())
        .withOperatorNormalization(Jsons.deserialize(record.get(OPERATION.OPERATOR_NORMALIZATION).data(), OperatorNormalization.class))
        .withOperatorDbt(Jsons.deserialize(record.get(OPERATION.OPERATOR_DBT).data(), OperatorDbt.class))
        .withTombstone(record.get(OPERATION.TOMBSTONE));
  }

  private List<ConfigWithMetadata<StandardSync>> listStandardSyncWithMetadata() throws IOException {
    return listStandardSyncWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardSync>> listStandardSyncWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(CONNECTION);
      if (configId.isPresent()) {
        return query.where(CONNECTION.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    final List<ConfigWithMetadata<StandardSync>> standardSyncs = new ArrayList<>();
    for (final Record record : result) {
      final StandardSync standardSync = DbConverter.buildStandardSync(record, connectionOperationIds(record.get(CONNECTION.ID)));
      if (ScheduleHelpers.isScheduleTypeMismatch(standardSync)) {
        throw new RuntimeException("unexpected schedule type mismatch");
      }
      standardSyncs.add(new ConfigWithMetadata<>(
          record.get(CONNECTION.ID).toString(),
          ConfigSchema.STANDARD_SYNC.name(),
          record.get(CONNECTION.CREATED_AT).toInstant(),
          record.get(CONNECTION.UPDATED_AT).toInstant(),
          standardSync));
    }
    return standardSyncs;
  }

  private List<ConfigWithMetadata<StandardSyncState>> listStandardSyncStateWithMetadata() throws IOException {
    return listStandardSyncStateWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<StandardSyncState>> listStandardSyncStateWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(STATE);
      if (configId.isPresent()) {
        return query.where(STATE.CONNECTION_ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });
    final List<ConfigWithMetadata<StandardSyncState>> standardSyncStates = new ArrayList<>();
    for (final Record record : result) {
      final StandardSyncState standardSyncState = buildStandardSyncState(record);
      standardSyncStates.add(new ConfigWithMetadata<>(
          record.get(STATE.CONNECTION_ID).toString(),
          ConfigSchema.STANDARD_SYNC_STATE.name(),
          record.get(STATE.CREATED_AT).toInstant(),
          record.get(STATE.UPDATED_AT).toInstant(),
          standardSyncState));
    }
    return standardSyncStates;
  }

  private StandardSyncState buildStandardSyncState(final Record record) {
    return new StandardSyncState()
        .withConnectionId(record.get(STATE.CONNECTION_ID))
        .withState(Jsons.deserialize(record.get(STATE.STATE_).data(), State.class));
  }

  private List<ConfigWithMetadata<ActorCatalog>> listActorCatalogWithMetadata() throws IOException {
    return listActorCatalogWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<ActorCatalog>> listActorCatalogWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_CATALOG);
      if (configId.isPresent()) {
        return query.where(ACTOR_CATALOG.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });
    final List<ConfigWithMetadata<ActorCatalog>> actorCatalogs = new ArrayList<>();
    for (final Record record : result) {
      final ActorCatalog actorCatalog = DbConverter.buildActorCatalog(record);
      actorCatalogs.add(new ConfigWithMetadata<>(
          record.get(ACTOR_CATALOG.ID).toString(),
          ConfigSchema.ACTOR_CATALOG.name(),
          record.get(ACTOR_CATALOG.CREATED_AT).toInstant(),
          record.get(ACTOR_CATALOG.MODIFIED_AT).toInstant(),
          actorCatalog));
    }
    return actorCatalogs;
  }

  private List<ConfigWithMetadata<ActorCatalogFetchEvent>> listActorCatalogFetchEventWithMetadata() throws IOException {
    return listActorCatalogFetchEventWithMetadata(Optional.empty());
  }

  private List<ConfigWithMetadata<ActorCatalogFetchEvent>> listActorCatalogFetchEventWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_CATALOG_FETCH_EVENT);
      if (configId.isPresent()) {
        return query.where(ACTOR_CATALOG_FETCH_EVENT.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });
    final List<ConfigWithMetadata<ActorCatalogFetchEvent>> actorCatalogFetchEvents = new ArrayList<>();
    for (final Record record : result) {
      final ActorCatalogFetchEvent actorCatalogFetchEvent = buildActorCatalogFetchEvent(record);
      actorCatalogFetchEvents.add(new ConfigWithMetadata<>(
          record.get(ACTOR_CATALOG_FETCH_EVENT.ID).toString(),
          ConfigSchema.ACTOR_CATALOG_FETCH_EVENT.name(),
          record.get(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT).toInstant(),
          record.get(ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT).toInstant(),
          actorCatalogFetchEvent));
    }
    return actorCatalogFetchEvents;
  }

  private ActorCatalogFetchEvent buildActorCatalogFetchEvent(final Record record) {
    return new ActorCatalogFetchEvent()
        .withId(record.get(ACTOR_CATALOG_FETCH_EVENT.ID))
        .withActorCatalogId(record.get(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID))
        .withConfigHash(record.get(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH))
        .withConnectorVersion(record.get(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION))
        .withActorId(record.get(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID));
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) throws JsonValidationException, IOException {
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      writeStandardWorkspace(Collections.singletonList((StandardWorkspace) config));
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      writeStandardSourceDefinition(Collections.singletonList((StandardSourceDefinition) config));
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      writeStandardDestinationDefinition(Collections.singletonList((StandardDestinationDefinition) config));
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      writeSourceConnection(Collections.singletonList((SourceConnection) config));
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      writeDestinationConnection(Collections.singletonList((DestinationConnection) config));
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      writeSourceOauthParameter(Collections.singletonList((SourceOAuthParameter) config));
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      writeDestinationOauthParameter(Collections.singletonList((DestinationOAuthParameter) config));
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      writeStandardSyncOperation(Collections.singletonList((StandardSyncOperation) config));
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      writeStandardSync(Collections.singletonList((StandardSync) config));
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      writeStandardSyncState(Collections.singletonList((StandardSyncState) config));
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      writeActorCatalog(Collections.singletonList((ActorCatalog) config));
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      writeActorCatalogFetchEvent(Collections.singletonList((ActorCatalogFetchEvent) config));
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      writeWorkspaceServiceAccount(Collections.singletonList((WorkspaceServiceAccount) config));
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  private void writeStandardWorkspace(final List<StandardWorkspace> configs) throws IOException {
    database.transaction(ctx -> {
      writeStandardWorkspace(configs, ctx);
      return null;
    });
  }

  private void writeStandardWorkspace(final List<StandardWorkspace> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardWorkspace) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(WORKSPACE)
          .where(WORKSPACE.ID.eq(standardWorkspace.getWorkspaceId())));

      if (isExistingConfig) {
        ctx.update(WORKSPACE)
            .set(WORKSPACE.ID, standardWorkspace.getWorkspaceId())
            .set(WORKSPACE.CUSTOMER_ID, standardWorkspace.getCustomerId())
            .set(WORKSPACE.NAME, standardWorkspace.getName())
            .set(WORKSPACE.SLUG, standardWorkspace.getSlug())
            .set(WORKSPACE.EMAIL, standardWorkspace.getEmail())
            .set(WORKSPACE.INITIAL_SETUP_COMPLETE, standardWorkspace.getInitialSetupComplete())
            .set(WORKSPACE.ANONYMOUS_DATA_COLLECTION, standardWorkspace.getAnonymousDataCollection())
            .set(WORKSPACE.SEND_NEWSLETTER, standardWorkspace.getNews())
            .set(WORKSPACE.SEND_SECURITY_UPDATES, standardWorkspace.getSecurityUpdates())
            .set(WORKSPACE.DISPLAY_SETUP_WIZARD, standardWorkspace.getDisplaySetupWizard())
            .set(WORKSPACE.TOMBSTONE, standardWorkspace.getTombstone() != null && standardWorkspace.getTombstone())
            .set(WORKSPACE.NOTIFICATIONS, JSONB.valueOf(Jsons.serialize(standardWorkspace.getNotifications())))
            .set(WORKSPACE.FIRST_SYNC_COMPLETE, standardWorkspace.getFirstCompletedSync())
            .set(WORKSPACE.FEEDBACK_COMPLETE, standardWorkspace.getFeedbackDone())
            .set(WORKSPACE.UPDATED_AT, timestamp)
            .where(WORKSPACE.ID.eq(standardWorkspace.getWorkspaceId()))
            .execute();
      } else {
        ctx.insertInto(WORKSPACE)
            .set(WORKSPACE.ID, standardWorkspace.getWorkspaceId())
            .set(WORKSPACE.CUSTOMER_ID, standardWorkspace.getCustomerId())
            .set(WORKSPACE.NAME, standardWorkspace.getName())
            .set(WORKSPACE.SLUG, standardWorkspace.getSlug())
            .set(WORKSPACE.EMAIL, standardWorkspace.getEmail())
            .set(WORKSPACE.INITIAL_SETUP_COMPLETE, standardWorkspace.getInitialSetupComplete())
            .set(WORKSPACE.ANONYMOUS_DATA_COLLECTION, standardWorkspace.getAnonymousDataCollection())
            .set(WORKSPACE.SEND_NEWSLETTER, standardWorkspace.getNews())
            .set(WORKSPACE.SEND_SECURITY_UPDATES, standardWorkspace.getSecurityUpdates())
            .set(WORKSPACE.DISPLAY_SETUP_WIZARD, standardWorkspace.getDisplaySetupWizard())
            .set(WORKSPACE.TOMBSTONE, standardWorkspace.getTombstone() != null && standardWorkspace.getTombstone())
            .set(WORKSPACE.NOTIFICATIONS, JSONB.valueOf(Jsons.serialize(standardWorkspace.getNotifications())))
            .set(WORKSPACE.FIRST_SYNC_COMPLETE, standardWorkspace.getFirstCompletedSync())
            .set(WORKSPACE.FEEDBACK_COMPLETE, standardWorkspace.getFeedbackDone())
            .set(WORKSPACE.CREATED_AT, timestamp)
            .set(WORKSPACE.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeWorkspaceServiceAccount(final List<WorkspaceServiceAccount> configs) throws IOException {
    database.transaction(ctx -> {
      writeWorkspaceServiceAccount(configs, ctx);
      return null;
    });
  }

  private void writeWorkspaceServiceAccount(final List<WorkspaceServiceAccount> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((workspaceServiceAccount) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(WORKSPACE_SERVICE_ACCOUNT)
          .where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(workspaceServiceAccount.getWorkspaceId())));

      if (isExistingConfig) {
        ctx.update(WORKSPACE_SERVICE_ACCOUNT)
            .set(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID, workspaceServiceAccount.getWorkspaceId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_ID, workspaceServiceAccount.getServiceAccountId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_EMAIL, workspaceServiceAccount.getServiceAccountEmail())
            .set(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getJsonCredential())))
            .set(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getHmacKey())))
            .set(WORKSPACE_SERVICE_ACCOUNT.UPDATED_AT, timestamp)
            .where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(workspaceServiceAccount.getWorkspaceId()))
            .execute();
      } else {
        ctx.insertInto(WORKSPACE_SERVICE_ACCOUNT)
            .set(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID, workspaceServiceAccount.getWorkspaceId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_ID, workspaceServiceAccount.getServiceAccountId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_EMAIL, workspaceServiceAccount.getServiceAccountEmail())
            .set(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getJsonCredential())))
            .set(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getHmacKey())))
            .set(WORKSPACE_SERVICE_ACCOUNT.CREATED_AT, timestamp)
            .set(WORKSPACE_SERVICE_ACCOUNT.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeStandardSourceDefinition(final List<StandardSourceDefinition> configs) throws IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardSourceDefinition(configs, ctx);
      return null;
    });
  }

  private void writeStandardDestinationDefinition(final List<StandardDestinationDefinition> configs) throws IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardDestinationDefinition(configs, ctx);
      return null;
    });
  }

  private void writeSourceConnection(final List<SourceConnection> configs) throws IOException {
    database.transaction(ctx -> {
      writeSourceConnection(configs, ctx);
      return null;
    });
  }

  private void writeSourceConnection(final List<SourceConnection> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((sourceConnection) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR)
          .where(ACTOR.ID.eq(sourceConnection.getSourceId())));

      if (isExistingConfig) {
        ctx.update(ACTOR)
            .set(ACTOR.ID, sourceConnection.getSourceId())
            .set(ACTOR.WORKSPACE_ID, sourceConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, sourceConnection.getSourceDefinitionId())
            .set(ACTOR.NAME, sourceConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.source)
            .set(ACTOR.TOMBSTONE, sourceConnection.getTombstone() != null && sourceConnection.getTombstone())
            .set(ACTOR.UPDATED_AT, timestamp)
            .where(ACTOR.ID.eq(sourceConnection.getSourceId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR)
            .set(ACTOR.ID, sourceConnection.getSourceId())
            .set(ACTOR.WORKSPACE_ID, sourceConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, sourceConnection.getSourceDefinitionId())
            .set(ACTOR.NAME, sourceConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.source)
            .set(ACTOR.TOMBSTONE, sourceConnection.getTombstone() != null && sourceConnection.getTombstone())
            .set(ACTOR.CREATED_AT, timestamp)
            .set(ACTOR.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeDestinationConnection(final List<DestinationConnection> configs) throws IOException {
    database.transaction(ctx -> {
      writeDestinationConnection(configs, ctx);
      return null;
    });
  }

  private void writeDestinationConnection(final List<DestinationConnection> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((destinationConnection) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR)
          .where(ACTOR.ID.eq(destinationConnection.getDestinationId())));

      if (isExistingConfig) {
        ctx.update(ACTOR)
            .set(ACTOR.ID, destinationConnection.getDestinationId())
            .set(ACTOR.WORKSPACE_ID, destinationConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, destinationConnection.getDestinationDefinitionId())
            .set(ACTOR.NAME, destinationConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR.TOMBSTONE, destinationConnection.getTombstone() != null && destinationConnection.getTombstone())
            .set(ACTOR.UPDATED_AT, timestamp)
            .where(ACTOR.ID.eq(destinationConnection.getDestinationId()))
            .execute();

      } else {
        ctx.insertInto(ACTOR)
            .set(ACTOR.ID, destinationConnection.getDestinationId())
            .set(ACTOR.WORKSPACE_ID, destinationConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, destinationConnection.getDestinationDefinitionId())
            .set(ACTOR.NAME, destinationConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR.TOMBSTONE, destinationConnection.getTombstone() != null && destinationConnection.getTombstone())
            .set(ACTOR.CREATED_AT, timestamp)
            .set(ACTOR.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeSourceOauthParameter(final List<SourceOAuthParameter> configs) throws IOException {
    database.transaction(ctx -> {
      writeSourceOauthParameter(configs, ctx);
      return null;
    });
  }

  private void writeSourceOauthParameter(final List<SourceOAuthParameter> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((sourceOAuthParameter) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_OAUTH_PARAMETER)
          .where(ACTOR_OAUTH_PARAMETER.ID.eq(sourceOAuthParameter.getOauthParameterId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, sourceOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, sourceOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, sourceOAuthParameter.getSourceDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.source)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .where(ACTOR_OAUTH_PARAMETER.ID.eq(sourceOAuthParameter.getOauthParameterId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, sourceOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, sourceOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, sourceOAuthParameter.getSourceDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.source)
            .set(ACTOR_OAUTH_PARAMETER.CREATED_AT, timestamp)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeDestinationOauthParameter(final List<DestinationOAuthParameter> configs) throws IOException {
    database.transaction(ctx -> {
      writeDestinationOauthParameter(configs, ctx);
      return null;
    });
  }

  private void writeDestinationOauthParameter(final List<DestinationOAuthParameter> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((destinationOAuthParameter) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_OAUTH_PARAMETER)
          .where(ACTOR_OAUTH_PARAMETER.ID.eq(destinationOAuthParameter.getOauthParameterId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, destinationOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, destinationOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, destinationOAuthParameter.getDestinationDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .where(ACTOR_OAUTH_PARAMETER.ID.eq(destinationOAuthParameter.getOauthParameterId()))
            .execute();

      } else {
        ctx.insertInto(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, destinationOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, destinationOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, destinationOAuthParameter.getDestinationDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR_OAUTH_PARAMETER.CREATED_AT, timestamp)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .execute();
      }
    });

  }

  private void writeStandardSyncOperation(final List<StandardSyncOperation> configs) throws IOException {
    database.transaction(ctx -> {
      writeStandardSyncOperation(configs, ctx);
      return null;
    });
  }

  private void writeStandardSyncOperation(final List<StandardSyncOperation> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardSyncOperation) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(OPERATION)
          .where(OPERATION.ID.eq(standardSyncOperation.getOperationId())));

      if (isExistingConfig) {
        ctx.update(OPERATION)
            .set(OPERATION.ID, standardSyncOperation.getOperationId())
            .set(OPERATION.WORKSPACE_ID, standardSyncOperation.getWorkspaceId())
            .set(OPERATION.NAME, standardSyncOperation.getName())
            .set(OPERATION.OPERATOR_TYPE, Enums.toEnum(standardSyncOperation.getOperatorType().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.OperatorType.class).orElseThrow())
            .set(OPERATION.OPERATOR_NORMALIZATION, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorNormalization())))
            .set(OPERATION.OPERATOR_DBT, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorDbt())))
            .set(OPERATION.TOMBSTONE, standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone())
            .set(OPERATION.UPDATED_AT, timestamp)
            .where(OPERATION.ID.eq(standardSyncOperation.getOperationId()))
            .execute();

      } else {
        ctx.insertInto(OPERATION)
            .set(OPERATION.ID, standardSyncOperation.getOperationId())
            .set(OPERATION.WORKSPACE_ID, standardSyncOperation.getWorkspaceId())
            .set(OPERATION.NAME, standardSyncOperation.getName())
            .set(OPERATION.OPERATOR_TYPE, Enums.toEnum(standardSyncOperation.getOperatorType().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.OperatorType.class).orElseThrow())
            .set(OPERATION.OPERATOR_NORMALIZATION, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorNormalization())))
            .set(OPERATION.OPERATOR_DBT, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorDbt())))
            .set(OPERATION.TOMBSTONE, standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone())
            .set(OPERATION.CREATED_AT, timestamp)
            .set(OPERATION.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeStandardSync(final List<StandardSync> configs) throws IOException {
    database.transaction(ctx -> {
      writeStandardSync(configs, ctx);
      return null;
    });
  }

  private void writeStandardSync(final List<StandardSync> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardSync) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(CONNECTION)
          .where(CONNECTION.ID.eq(standardSync.getConnectionId())));

      if (ScheduleHelpers.isScheduleTypeMismatch(standardSync)) {
        throw new RuntimeException("unexpected schedule type mismatch");
      }

      if (isExistingConfig) {
        ctx.update(CONNECTION)
            .set(CONNECTION.ID, standardSync.getConnectionId())
            .set(CONNECTION.NAMESPACE_DEFINITION, Enums.toEnum(standardSync.getNamespaceDefinition().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType.class).orElseThrow())
            .set(CONNECTION.NAMESPACE_FORMAT, standardSync.getNamespaceFormat())
            .set(CONNECTION.PREFIX, standardSync.getPrefix())
            .set(CONNECTION.SOURCE_ID, standardSync.getSourceId())
            .set(CONNECTION.DESTINATION_ID, standardSync.getDestinationId())
            .set(CONNECTION.NAME, standardSync.getName())
            .set(CONNECTION.CATALOG, JSONB.valueOf(Jsons.serialize(standardSync.getCatalog())))
            .set(CONNECTION.STATUS, standardSync.getStatus() == null ? null
                : Enums.toEnum(standardSync.getStatus().value(),
                    io.airbyte.db.instance.configs.jooq.generated.enums.StatusType.class).orElseThrow())
            .set(CONNECTION.SCHEDULE, JSONB.valueOf(Jsons.serialize(standardSync.getSchedule())))
            .set(CONNECTION.MANUAL, standardSync.getManual())
            .set(CONNECTION.SCHEDULE_TYPE,
                standardSync.getScheduleType() == null ? null
                    : Enums.toEnum(standardSync.getScheduleType().value(), io.airbyte.db.instance.configs.jooq.generated.enums.ScheduleType.class)
                        .orElseThrow())
            .set(CONNECTION.SCHEDULE_DATA, JSONB.valueOf(Jsons.serialize(standardSync.getScheduleData())))
            .set(CONNECTION.RESOURCE_REQUIREMENTS, JSONB.valueOf(Jsons.serialize(standardSync.getResourceRequirements())))
            .set(CONNECTION.UPDATED_AT, timestamp)
            .set(CONNECTION.SOURCE_CATALOG_ID, standardSync.getSourceCatalogId())
            .where(CONNECTION.ID.eq(standardSync.getConnectionId()))
            .execute();

        ctx.deleteFrom(CONNECTION_OPERATION)
            .where(CONNECTION_OPERATION.CONNECTION_ID.eq(standardSync.getConnectionId()))
            .execute();
        for (final UUID operationIdFromStandardSync : standardSync.getOperationIds()) {
          ctx.insertInto(CONNECTION_OPERATION)
              .set(CONNECTION_OPERATION.ID, UUID.randomUUID())
              .set(CONNECTION_OPERATION.CONNECTION_ID, standardSync.getConnectionId())
              .set(CONNECTION_OPERATION.OPERATION_ID, operationIdFromStandardSync)
              .set(CONNECTION_OPERATION.CREATED_AT, timestamp)
              .set(CONNECTION_OPERATION.UPDATED_AT, timestamp)
              .execute();
        }
      } else {
        ctx.insertInto(CONNECTION)
            .set(CONNECTION.ID, standardSync.getConnectionId())
            .set(CONNECTION.NAMESPACE_DEFINITION, Enums.toEnum(standardSync.getNamespaceDefinition().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType.class).orElseThrow())
            .set(CONNECTION.NAMESPACE_FORMAT, standardSync.getNamespaceFormat())
            .set(CONNECTION.PREFIX, standardSync.getPrefix())
            .set(CONNECTION.SOURCE_ID, standardSync.getSourceId())
            .set(CONNECTION.DESTINATION_ID, standardSync.getDestinationId())
            .set(CONNECTION.NAME, standardSync.getName())
            .set(CONNECTION.CATALOG, JSONB.valueOf(Jsons.serialize(standardSync.getCatalog())))
            .set(CONNECTION.STATUS, standardSync.getStatus() == null ? null
                : Enums.toEnum(standardSync.getStatus().value(),
                    io.airbyte.db.instance.configs.jooq.generated.enums.StatusType.class).orElseThrow())
            .set(CONNECTION.SCHEDULE, JSONB.valueOf(Jsons.serialize(standardSync.getSchedule())))
            .set(CONNECTION.MANUAL, standardSync.getManual())
            .set(CONNECTION.SCHEDULE_TYPE,
                standardSync.getScheduleType() == null ? null
                    : Enums.toEnum(standardSync.getScheduleType().value(), io.airbyte.db.instance.configs.jooq.generated.enums.ScheduleType.class)
                        .orElseThrow())
            .set(CONNECTION.SCHEDULE_DATA, JSONB.valueOf(Jsons.serialize(standardSync.getScheduleData())))
            .set(CONNECTION.RESOURCE_REQUIREMENTS, JSONB.valueOf(Jsons.serialize(standardSync.getResourceRequirements())))
            .set(CONNECTION.SOURCE_CATALOG_ID, standardSync.getSourceCatalogId())
            .set(CONNECTION.CREATED_AT, timestamp)
            .set(CONNECTION.UPDATED_AT, timestamp)
            .execute();
        for (final UUID operationIdFromStandardSync : standardSync.getOperationIds()) {
          ctx.insertInto(CONNECTION_OPERATION)
              .set(CONNECTION_OPERATION.ID, UUID.randomUUID())
              .set(CONNECTION_OPERATION.CONNECTION_ID, standardSync.getConnectionId())
              .set(CONNECTION_OPERATION.OPERATION_ID, operationIdFromStandardSync)
              .set(CONNECTION_OPERATION.CREATED_AT, timestamp)
              .set(CONNECTION_OPERATION.UPDATED_AT, timestamp)
              .execute();
        }
      }
    });
  }

  private void writeStandardSyncState(final List<StandardSyncState> configs) throws IOException {
    database.transaction(ctx -> {
      writeStandardSyncState(configs, ctx);
      return null;
    });
  }

  private void writeStandardSyncState(final List<StandardSyncState> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardSyncState) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(STATE)
          .where(STATE.CONNECTION_ID.eq(standardSyncState.getConnectionId())));

      if (isExistingConfig) {
        ctx.update(STATE)
            .set(STATE.CONNECTION_ID, standardSyncState.getConnectionId())
            .set(STATE.STATE_, JSONB.valueOf(Jsons.serialize(standardSyncState.getState())))
            .set(STATE.UPDATED_AT, timestamp)
            .where(STATE.CONNECTION_ID.eq(standardSyncState.getConnectionId()))
            .execute();
      } else {
        ctx.insertInto(STATE)
            .set(STATE.ID, UUID.randomUUID())
            .set(STATE.CONNECTION_ID, standardSyncState.getConnectionId())
            .set(STATE.STATE_, JSONB.valueOf(Jsons.serialize(standardSyncState.getState())))
            .set(STATE.CREATED_AT, timestamp)
            .set(STATE.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeActorCatalog(final List<ActorCatalog> configs) throws IOException {
    database.transaction(ctx -> {
      writeActorCatalog(configs, ctx);
      return null;
    });
  }

  private void writeActorCatalog(final List<ActorCatalog> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((actorCatalog) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_CATALOG)
          .where(ACTOR_CATALOG.ID.eq(actorCatalog.getId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_CATALOG)
            .set(ACTOR_CATALOG.CATALOG, JSONB.valueOf(Jsons.serialize(actorCatalog.getCatalog())))
            .set(ACTOR_CATALOG.CATALOG_HASH, actorCatalog.getCatalogHash())
            .set(ACTOR_CATALOG.MODIFIED_AT, timestamp)
            .where(ACTOR_CATALOG.ID.eq(actorCatalog.getId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR_CATALOG)
            .set(ACTOR_CATALOG.ID, actorCatalog.getId())
            .set(ACTOR_CATALOG.CATALOG, JSONB.valueOf(Jsons.serialize(actorCatalog.getCatalog())))
            .set(ACTOR_CATALOG.CATALOG_HASH, actorCatalog.getCatalogHash())
            .set(ACTOR_CATALOG.CREATED_AT, timestamp)
            .set(ACTOR_CATALOG.MODIFIED_AT, timestamp)
            .execute();
      }
    });
  }

  private void writeActorCatalogFetchEvent(final List<ActorCatalogFetchEvent> configs) throws IOException {
    database.transaction(ctx -> {
      writeActorCatalogFetchEvent(configs, ctx);
      return null;
    });
  }

  private void writeActorCatalogFetchEvent(final List<ActorCatalogFetchEvent> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((actorCatalogFetchEvent) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_CATALOG_FETCH_EVENT)
          .where(ACTOR_CATALOG_FETCH_EVENT.ID.eq(actorCatalogFetchEvent.getId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_CATALOG_FETCH_EVENT)
            .set(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH, actorCatalogFetchEvent.getConfigHash())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID, actorCatalogFetchEvent.getActorCatalogId())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID, actorCatalogFetchEvent.getActorId())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION, actorCatalogFetchEvent.getConnectorVersion())
            .set(ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT, timestamp)
            .where(ACTOR_CATALOG_FETCH_EVENT.ID.eq(actorCatalogFetchEvent.getId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR_CATALOG_FETCH_EVENT)
            .set(ACTOR_CATALOG_FETCH_EVENT.ID, actorCatalogFetchEvent.getId())
            .set(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH, actorCatalogFetchEvent.getConfigHash())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID, actorCatalogFetchEvent.getActorCatalogId())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID, actorCatalogFetchEvent.getActorId())
            .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION, actorCatalogFetchEvent.getConnectorVersion())
            .set(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT, timestamp)
            .set(ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT, timestamp)
            .execute();
      }
    });
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) throws IOException, JsonValidationException {
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      writeStandardWorkspace(configs.values().stream().map(c -> (StandardWorkspace) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      writeStandardSourceDefinition(configs.values().stream().map(c -> (StandardSourceDefinition) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      writeStandardDestinationDefinition(configs.values().stream().map(c -> (StandardDestinationDefinition) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      writeSourceConnection(configs.values().stream().map(c -> (SourceConnection) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      writeDestinationConnection(configs.values().stream().map(c -> (DestinationConnection) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      writeSourceOauthParameter(configs.values().stream().map(c -> (SourceOAuthParameter) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      writeDestinationOauthParameter(configs.values().stream().map(c -> (DestinationOAuthParameter) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      writeStandardSyncOperation(configs.values().stream().map(c -> (StandardSyncOperation) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      writeStandardSync(configs.values().stream().map(c -> (StandardSync) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      writeStandardSyncState(configs.values().stream().map(c -> (StandardSyncState) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      writeActorCatalog(configs.values().stream().map(c -> (ActorCatalog) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      writeActorCatalogFetchEvent(configs.values().stream().map(c -> (ActorCatalogFetchEvent) c).collect(Collectors.toList()));
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      writeWorkspaceServiceAccount(configs.values().stream().map(c -> (WorkspaceServiceAccount) c).collect(Collectors.toList()));
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) throws ConfigNotFoundException, IOException {
    if (configType == ConfigSchema.STANDARD_WORKSPACE) {
      deleteConfig(WORKSPACE, WORKSPACE.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      deleteConfig(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      deleteConfig(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.SOURCE_CONNECTION) {
      deleteConfig(ACTOR, ACTOR.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.DESTINATION_CONNECTION) {
      deleteConfig(ACTOR, ACTOR.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.SOURCE_OAUTH_PARAM) {
      deleteConfig(ACTOR_OAUTH_PARAMETER, ACTOR_OAUTH_PARAMETER.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.DESTINATION_OAUTH_PARAM) {
      deleteConfig(ACTOR_OAUTH_PARAMETER, ACTOR_OAUTH_PARAMETER.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.STANDARD_SYNC_OPERATION) {
      deleteConfig(OPERATION, OPERATION.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.STANDARD_SYNC) {
      deleteStandardSync(configId);
    } else if (configType == ConfigSchema.STANDARD_SYNC_STATE) {
      deleteConfig(STATE, STATE.CONNECTION_ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.ACTOR_CATALOG) {
      deleteConfig(ACTOR_CATALOG, ACTOR_CATALOG.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.ACTOR_CATALOG_FETCH_EVENT) {
      deleteConfig(ACTOR_CATALOG_FETCH_EVENT, ACTOR_CATALOG_FETCH_EVENT.ID, UUID.fromString(configId));
    } else if (configType == ConfigSchema.WORKSPACE_SERVICE_ACCOUNT) {
      deleteConfig(WORKSPACE_SERVICE_ACCOUNT, WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID, UUID.fromString(configId));
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  private <T extends Record> void deleteConfig(final TableImpl<T> table, final TableField<T, UUID> keyColumn, final UUID configId)
      throws IOException {
    database.transaction(ctx -> {
      deleteConfig(table, keyColumn, configId, ctx);
      return null;
    });
  }

  private <T extends Record> void deleteConfig(final TableImpl<T> table,
                                               final TableField<T, UUID> keyColumn,
                                               final UUID configId,
                                               final DSLContext ctx) {
    final boolean isExistingConfig = ctx.fetchExists(select()
        .from(table)
        .where(keyColumn.eq(configId)));

    if (isExistingConfig) {
      ctx.deleteFrom(table)
          .where(keyColumn.eq(configId))
          .execute();
    }
  }

  private void deleteStandardSync(final String configId) throws IOException {
    database.transaction(ctx -> {
      final UUID connectionId = UUID.fromString(configId);
      deleteConfig(CONNECTION_OPERATION, CONNECTION_OPERATION.CONNECTION_ID, connectionId, ctx);
      deleteConfig(STATE, STATE.CONNECTION_ID, connectionId, ctx);
      deleteConfig(CONNECTION, CONNECTION.ID, connectionId, ctx);
      return null;
    });
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    if (dryRun) {
      return;
    }

    LOGGER.info("Replacing all configs");
    final Set<AirbyteConfig> originalConfigs = new HashSet<>(configs.keySet());
    database.transaction(ctx -> {
      ctx.truncate(WORKSPACE).restartIdentity().cascade().execute();
      ctx.truncate(ACTOR_DEFINITION).restartIdentity().cascade().execute();
      ctx.truncate(ACTOR).restartIdentity().cascade().execute();
      ctx.truncate(ACTOR_OAUTH_PARAMETER).restartIdentity().cascade().execute();
      ctx.truncate(OPERATION).restartIdentity().cascade().execute();
      ctx.truncate(CONNECTION).restartIdentity().cascade().execute();
      ctx.truncate(CONNECTION_OPERATION).restartIdentity().cascade().execute();
      ctx.truncate(STATE).restartIdentity().cascade().execute();
      ctx.truncate(ACTOR_CATALOG).restartIdentity().cascade().execute();
      ctx.truncate(ACTOR_CATALOG_FETCH_EVENT).restartIdentity().cascade().execute();
      ctx.truncate(WORKSPACE_SERVICE_ACCOUNT).restartIdentity().cascade().execute();

      if (configs.containsKey(ConfigSchema.STANDARD_WORKSPACE)) {
        configs.get(ConfigSchema.STANDARD_WORKSPACE).map(c -> (StandardWorkspace) c)
            .forEach(c -> writeStandardWorkspace(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_WORKSPACE);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_WORKSPACE + NOT_FOUND);
      }
      if (configs.containsKey(ConfigSchema.STANDARD_SOURCE_DEFINITION)) {
        configs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION).map(c -> (StandardSourceDefinition) c)
            .forEach(c -> ConfigWriter.writeStandardSourceDefinition(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_SOURCE_DEFINITION);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_SOURCE_DEFINITION + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.STANDARD_DESTINATION_DEFINITION)) {
        configs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION).map(c -> (StandardDestinationDefinition) c)
            .forEach(c -> ConfigWriter.writeStandardDestinationDefinition(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_DESTINATION_DEFINITION);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_DESTINATION_DEFINITION + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.SOURCE_CONNECTION)) {
        configs.get(ConfigSchema.SOURCE_CONNECTION).map(c -> (SourceConnection) c)
            .forEach(c -> writeSourceConnection(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.SOURCE_CONNECTION);
      } else {
        LOGGER.warn(ConfigSchema.SOURCE_CONNECTION + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.DESTINATION_CONNECTION)) {
        configs.get(ConfigSchema.DESTINATION_CONNECTION).map(c -> (DestinationConnection) c)
            .forEach(c -> writeDestinationConnection(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.DESTINATION_CONNECTION);
      } else {
        LOGGER.warn(ConfigSchema.DESTINATION_CONNECTION + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.SOURCE_OAUTH_PARAM)) {
        configs.get(ConfigSchema.SOURCE_OAUTH_PARAM).map(c -> (SourceOAuthParameter) c)
            .forEach(c -> writeSourceOauthParameter(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.SOURCE_OAUTH_PARAM);
      } else {
        LOGGER.warn(ConfigSchema.SOURCE_OAUTH_PARAM + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.DESTINATION_OAUTH_PARAM)) {
        configs.get(ConfigSchema.DESTINATION_OAUTH_PARAM).map(c -> (DestinationOAuthParameter) c)
            .forEach(c -> writeDestinationOauthParameter(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.DESTINATION_OAUTH_PARAM);
      } else {
        LOGGER.warn(ConfigSchema.DESTINATION_OAUTH_PARAM + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.STANDARD_SYNC_OPERATION)) {
        configs.get(ConfigSchema.STANDARD_SYNC_OPERATION).map(c -> (StandardSyncOperation) c)
            .forEach(c -> writeStandardSyncOperation(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_SYNC_OPERATION);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_SYNC_OPERATION + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.ACTOR_CATALOG)) {
        configs.get(ConfigSchema.ACTOR_CATALOG).map(c -> (ActorCatalog) c)
            .forEach(c -> writeActorCatalog(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.ACTOR_CATALOG);
      } else {
        LOGGER.warn(ConfigSchema.ACTOR_CATALOG + NOT_FOUND);
      }
      if (configs.containsKey(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT)) {
        configs.get(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT).map(c -> (ActorCatalogFetchEvent) c)
            .forEach(c -> writeActorCatalogFetchEvent(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT);
      } else {
        LOGGER.warn(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT + NOT_FOUND);
      }

      // Syncs need to be imported after Actor Catalogs as they have a foreign key association with Actor
      // Catalogs.
      // e.g. They reference catalogs and thus catalogs need to exist before or the insert will fail.
      if (configs.containsKey(ConfigSchema.STANDARD_SYNC)) {
        configs.get(ConfigSchema.STANDARD_SYNC).map(c -> (StandardSync) c).forEach(c -> writeStandardSync(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_SYNC);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_SYNC + NOT_FOUND);
      }

      if (configs.containsKey(ConfigSchema.STANDARD_SYNC_STATE)) {
        configs.get(ConfigSchema.STANDARD_SYNC_STATE).map(c -> (StandardSyncState) c)
            .forEach(c -> writeStandardSyncState(Collections.singletonList(c), ctx));
        originalConfigs.remove(ConfigSchema.STANDARD_SYNC_STATE);
      } else {
        LOGGER.warn(ConfigSchema.STANDARD_SYNC_STATE + NOT_FOUND);
      }

      if (!originalConfigs.isEmpty()) {
        originalConfigs.forEach(c -> LOGGER.warn("Unknown Config " + c + " ignored"));
      }

      return null;
    });

    LOGGER.info("Config database is reset");
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    LOGGER.info("Exporting all configs...");

    final Map<String, Stream<JsonNode>> result = new HashMap<>();
    final List<ConfigWithMetadata<StandardWorkspace>> standardWorkspaceWithMetadata = listStandardWorkspaceWithMetadata();
    if (!standardWorkspaceWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_WORKSPACE.name(),
          standardWorkspaceWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<StandardSourceDefinition>> standardSourceDefinitionWithMetadata = listStandardSourceDefinitionWithMetadata();
    if (!standardSourceDefinitionWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
          standardSourceDefinitionWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<StandardDestinationDefinition>> standardDestinationDefinitionWithMetadata =
        listStandardDestinationDefinitionWithMetadata();
    if (!standardDestinationDefinitionWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(),
          standardDestinationDefinitionWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<SourceConnection>> sourceConnectionWithMetadata = listSourceConnectionWithMetadata();
    if (!sourceConnectionWithMetadata.isEmpty()) {
      result.put(ConfigSchema.SOURCE_CONNECTION.name(),
          sourceConnectionWithMetadata
              .stream()
              .map(configWithMetadata -> {
                try {
                  final UUID sourceDefinitionId = configWithMetadata.getConfig().getSourceDefinitionId();
                  final StandardSourceDefinition standardSourceDefinition = getConfig(
                      ConfigSchema.STANDARD_SOURCE_DEFINITION,
                      sourceDefinitionId.toString(),
                      StandardSourceDefinition.class);

                  final JsonNode connectionSpecs = standardSourceDefinition.getSpec().getConnectionSpecification();
                  final JsonNode sanitizedConfig =
                      jsonSecretsProcessor.prepareSecretsForOutput(configWithMetadata.getConfig().getConfiguration(), connectionSpecs);

                  configWithMetadata.getConfig().setConfiguration(sanitizedConfig);
                  return Jsons.jsonNode(configWithMetadata.getConfig());
                } catch (final ConfigNotFoundException | JsonValidationException | IOException e) {
                  throw new RuntimeException(e);
                }
              }));
    }
    final List<ConfigWithMetadata<DestinationConnection>> destinationConnectionWithMetadata = listDestinationConnectionWithMetadata();
    if (!destinationConnectionWithMetadata.isEmpty()) {
      final Stream<JsonNode> jsonNodeStream = destinationConnectionWithMetadata
          .stream()
          .map(configWithMetadata -> {
            try {
              final UUID destinationDefinition = configWithMetadata.getConfig().getDestinationDefinitionId();
              final StandardDestinationDefinition standardDestinationDefinition = getConfig(
                  ConfigSchema.STANDARD_DESTINATION_DEFINITION,
                  destinationDefinition.toString(),
                  StandardDestinationDefinition.class);
              final JsonNode connectionSpecs = standardDestinationDefinition.getSpec().getConnectionSpecification();
              final JsonNode sanitizedConfig =
                  jsonSecretsProcessor.prepareSecretsForOutput(configWithMetadata.getConfig().getConfiguration(), connectionSpecs);

              configWithMetadata.getConfig().setConfiguration(sanitizedConfig);
              return Jsons.jsonNode(configWithMetadata.getConfig());
            } catch (final ConfigNotFoundException | JsonValidationException | IOException e) {
              throw new RuntimeException(e);
            }
          });
      result.put(ConfigSchema.DESTINATION_CONNECTION.name(), jsonNodeStream);

    }
    final List<ConfigWithMetadata<SourceOAuthParameter>> sourceOauthParamWithMetadata = listSourceOauthParamWithMetadata();
    if (!sourceOauthParamWithMetadata.isEmpty()) {
      result.put(ConfigSchema.SOURCE_OAUTH_PARAM.name(),
          sourceOauthParamWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<DestinationOAuthParameter>> destinationOauthParamWithMetadata = listDestinationOauthParamWithMetadata();
    if (!destinationOauthParamWithMetadata.isEmpty()) {
      result.put(ConfigSchema.DESTINATION_OAUTH_PARAM.name(),
          destinationOauthParamWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<StandardSyncOperation>> standardSyncOperationWithMetadata = listStandardSyncOperationWithMetadata();
    if (!standardSyncOperationWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_SYNC_OPERATION.name(),
          standardSyncOperationWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<StandardSync>> standardSyncWithMetadata = listStandardSyncWithMetadata();
    if (!standardSyncWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_SYNC.name(),
          standardSyncWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<StandardSyncState>> standardSyncStateWithMetadata = listStandardSyncStateWithMetadata();
    if (!standardSyncStateWithMetadata.isEmpty()) {
      result.put(ConfigSchema.STANDARD_SYNC_STATE.name(),
          standardSyncStateWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<ActorCatalog>> actorCatalogWithMetadata = listActorCatalogWithMetadata();
    if (!actorCatalogWithMetadata.isEmpty()) {
      result.put(ConfigSchema.ACTOR_CATALOG.name(),
          actorCatalogWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    final List<ConfigWithMetadata<ActorCatalogFetchEvent>> actorCatalogFetchEventWithMetadata = listActorCatalogFetchEventWithMetadata();
    if (!actorCatalogFetchEventWithMetadata.isEmpty()) {
      result.put(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT.name(),
          actorCatalogFetchEventWithMetadata
              .stream()
              .map(ConfigWithMetadata::getConfig)
              .map(Jsons::jsonNode));
    }
    return result;
  }

  @Override
  public void loadData(final ConfigPersistence seedConfigPersistence) throws IOException {
    database.transaction(ctx -> {
      updateConfigsFromSeed(ctx, seedConfigPersistence);
      return null;
    });
  }

  @VisibleForTesting
  void updateConfigsFromSeed(final DSLContext ctx, final ConfigPersistence seedConfigPersistence) throws SQLException {
    LOGGER.info("Updating connector definitions from the seed if necessary...");

    try {
      final Set<String> connectorRepositoriesInUse = getConnectorRepositoriesInUse(ctx);
      LOGGER.info("Connectors in use: {}", connectorRepositoriesInUse);

      final Map<String, ConnectorInfo> connectorRepositoryToInfoMap = getConnectorRepositoryToInfoMap(ctx);
      LOGGER.info("Current connector versions: {}", connectorRepositoryToInfoMap.values());

      int newConnectorCount = 0;
      int updatedConnectorCount = 0;

      final List<StandardSourceDefinition> latestSources = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
      final ConnectorCounter sourceConnectorCounter = updateConnectorDefinitions(ctx, ConfigSchema.STANDARD_SOURCE_DEFINITION,
          latestSources, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += sourceConnectorCounter.newCount;
      updatedConnectorCount += sourceConnectorCounter.updateCount;

      final List<StandardDestinationDefinition> latestDestinations = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
      final ConnectorCounter destinationConnectorCounter = updateConnectorDefinitions(ctx, ConfigSchema.STANDARD_DESTINATION_DEFINITION,
          latestDestinations, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += destinationConnectorCounter.newCount;
      updatedConnectorCount += destinationConnectorCounter.updateCount;

      LOGGER.info("Connector definitions have been updated ({} new connectors, and {} updates)", newConnectorCount, updatedConnectorCount);
    } catch (final IOException | JsonValidationException e) {
      throw new SQLException(e);
    }
  }

  /**
   * @return A set of connectors (both source and destination) that are already used in standard
   *         syncs. We identify connectors by its repository name instead of definition id because
   *         connectors can be added manually by users, and their config ids are not always the same
   *         as those in the seed.
   */
  private Set<String> getConnectorRepositoriesInUse(final DSLContext ctx) {
    final Set<UUID> usedConnectorDefinitionIds = ctx
        .select(ACTOR.ACTOR_DEFINITION_ID)
        .from(ACTOR)
        .fetch()
        .stream()
        .flatMap(row -> Stream.of(row.value1()))
        .collect(Collectors.toSet());

    return ctx.select(ACTOR_DEFINITION.DOCKER_REPOSITORY)
        .from(ACTOR_DEFINITION)
        .where(ACTOR_DEFINITION.ID.in(usedConnectorDefinitionIds))
        .fetch().stream()
        .map(Record1::value1)
        .collect(Collectors.toSet());
  }

  /**
   * @return A map about current connectors (both source and destination). It maps from connector
   *         repository to its definition id and docker image tag. We identify a connector by its
   *         repository name instead of definition id because connectors can be added manually by
   *         users, and are not always the same as those in the seed.
   */
  @VisibleForTesting
  Map<String, ConnectorInfo> getConnectorRepositoryToInfoMap(final DSLContext ctx) {
    return ctx.select(asterisk())
        .from(ACTOR_DEFINITION)
        .where(ACTOR_DEFINITION.RELEASE_STAGE.isNull()
            .or(ACTOR_DEFINITION.RELEASE_STAGE.ne(ReleaseStage.custom).or(ACTOR_DEFINITION.CUSTOM)))
        .fetch()
        .stream()
        .collect(Collectors.toMap(
            row -> row.getValue(ACTOR_DEFINITION.DOCKER_REPOSITORY),
            row -> {
              final JsonNode jsonNode;
              if (row.get(ACTOR_DEFINITION.ACTOR_TYPE) == ActorType.source) {
                jsonNode = Jsons.jsonNode(new StandardSourceDefinition()
                    .withSourceDefinitionId(row.get(ACTOR_DEFINITION.ID))
                    .withDockerImageTag(row.get(ACTOR_DEFINITION.DOCKER_IMAGE_TAG))
                    .withIcon(row.get(ACTOR_DEFINITION.ICON))
                    .withDockerRepository(row.get(ACTOR_DEFINITION.DOCKER_REPOSITORY))
                    .withDocumentationUrl(row.get(ACTOR_DEFINITION.DOCUMENTATION_URL))
                    .withName(row.get(ACTOR_DEFINITION.NAME))
                    .withPublic(row.get(ACTOR_DEFINITION.PUBLIC))
                    .withCustom(row.get(ACTOR_DEFINITION.CUSTOM))
                    .withSourceType(row.get(ACTOR_DEFINITION.SOURCE_TYPE) == null ? null
                        : Enums.toEnum(row.get(ACTOR_DEFINITION.SOURCE_TYPE, String.class), SourceType.class).orElseThrow())
                    .withSpec(Jsons.deserialize(row.get(ACTOR_DEFINITION.SPEC).data(), ConnectorSpecification.class)));
              } else if (row.get(ACTOR_DEFINITION.ACTOR_TYPE) == ActorType.destination) {
                jsonNode = Jsons.jsonNode(new StandardDestinationDefinition()
                    .withDestinationDefinitionId(row.get(ACTOR_DEFINITION.ID))
                    .withDockerImageTag(row.get(ACTOR_DEFINITION.DOCKER_IMAGE_TAG))
                    .withIcon(row.get(ACTOR_DEFINITION.ICON))
                    .withDockerRepository(row.get(ACTOR_DEFINITION.DOCKER_REPOSITORY))
                    .withDocumentationUrl(row.get(ACTOR_DEFINITION.DOCUMENTATION_URL))
                    .withName(row.get(ACTOR_DEFINITION.NAME))
                    .withPublic(row.get(ACTOR_DEFINITION.PUBLIC))
                    .withCustom(row.get(ACTOR_DEFINITION.CUSTOM))
                    .withSpec(Jsons.deserialize(row.get(ACTOR_DEFINITION.SPEC).data(), ConnectorSpecification.class)));
              } else {
                throw new RuntimeException("Unknown Actor Type " + row.get(ACTOR_DEFINITION.ACTOR_TYPE));
              }
              return new ConnectorInfo(row.getValue(ACTOR_DEFINITION.ID).toString(), jsonNode);
            },
            (c1, c2) -> {
              final AirbyteVersion v1 = new AirbyteVersion(c1.dockerImageTag);
              final AirbyteVersion v2 = new AirbyteVersion(c2.dockerImageTag);
              LOGGER.warn("Duplicated connector version found for {}: {} ({}) vs {} ({})",
                  c1.dockerRepository, c1.dockerImageTag, c1.definitionId, c2.dockerImageTag, c2.definitionId);
              final int comparison = v1.patchVersionCompareTo(v2);
              if (comparison >= 0) {
                return c1;
              } else {
                return c2;
              }
            }));
  }

  /**
   * The custom connector are not present in the seed and thus it is not relevant to validate their
   * latest version. This method allows to filter them out.
   *
   * @param connectorRepositoryToIdVersionMap
   * @param configType
   * @return
   */
  @VisibleForTesting
  Map<String, ConnectorInfo> filterCustomConnector(final Map<String, ConnectorInfo> connectorRepositoryToIdVersionMap,
                                                   final AirbyteConfig configType) {
    return connectorRepositoryToIdVersionMap.entrySet().stream()
        // The validation is based on the of the connector name is based on the seed which doesn't contain
        // any custom connectors. They can thus be
        // filtered out.
        .filter(entry -> {
          if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
            return !Jsons.object(entry.getValue().definition, StandardSourceDefinition.class).getCustom();
          } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
            return !Jsons.object(entry.getValue().definition, StandardDestinationDefinition.class).getCustom();
          } else {
            return true;
          }
        })
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
  }

  /**
   * @param connectorRepositoriesInUse when a connector is used in any standard sync, its definition
   *        will not be updated. This is necessary because the new connector version may not be
   *        backward compatible.
   */
  @VisibleForTesting
  <T> ConnectorCounter updateConnectorDefinitions(final DSLContext ctx,
                                                  final AirbyteConfig configType,
                                                  final List<T> latestDefinitions,
                                                  final Set<String> connectorRepositoriesInUse,
                                                  final Map<String, ConnectorInfo> connectorRepositoryToIdVersionMap)
      throws IOException {
    int newCount = 0;
    int updatedCount = 0;

    for (final T definition : latestDefinitions) {
      final JsonNode latestDefinition = Jsons.jsonNode(definition);
      final String repository = latestDefinition.get("dockerRepository").asText();

      final Map<String, ConnectorInfo> connectorRepositoryToIdVersionMapWithoutCustom = filterCustomConnector(connectorRepositoryToIdVersionMap,
          configType);

      // Add new connector
      if (!connectorRepositoryToIdVersionMapWithoutCustom.containsKey(repository)) {
        LOGGER.info("Adding new connector {}: {}", repository, latestDefinition);
        writeOrUpdateStandardDefinition(ctx, configType, latestDefinition);
        newCount++;
        continue;
      }

      final ConnectorInfo connectorInfo = connectorRepositoryToIdVersionMapWithoutCustom.get(repository);
      final JsonNode currentDefinition = connectorInfo.definition;

      // todo (lmossman) - this logic to remove the "spec" field is temporary; it is necessary to avoid
      // breaking users who are actively using an old connector version, otherwise specs from the most
      // recent connector versions may be inserted into the db which could be incompatible with the
      // version they are actually using.
      // Once the faux major version bump has been merged, this "new field" logic will be removed
      // entirely.
      final Set<String> newFields = Sets.difference(getNewFields(currentDefinition, latestDefinition), Set.of("spec"));

      // Process connector in use
      if (connectorRepositoriesInUse.contains(repository)) {
        final String latestImageTag = latestDefinition.get("dockerImageTag").asText();
        if (hasNewPatchVersion(connectorInfo.dockerImageTag, latestImageTag)) {
          // Update connector to the latest patch version
          LOGGER.info("Connector {} needs update: {} vs {}", repository, connectorInfo.dockerImageTag, latestImageTag);
          writeOrUpdateStandardDefinition(ctx, configType, latestDefinition);
          updatedCount++;
        } else if (newFields.isEmpty()) {
          LOGGER.info("Connector {} is in use and has all fields; skip updating", repository);
        } else {
          // Add new fields to the connector definition
          final JsonNode definitionToUpdate = getDefinitionWithNewFields(currentDefinition, latestDefinition, newFields);
          LOGGER.info("Connector {} has new fields: {}", repository, String.join(", ", newFields));
          writeOrUpdateStandardDefinition(ctx, configType, definitionToUpdate);
          updatedCount++;
        }
        continue;
      }

      // Process unused connector
      final String latestImageTag = latestDefinition.get("dockerImageTag").asText();
      if (hasNewVersion(connectorInfo.dockerImageTag, latestImageTag)) {
        // Update connector to the latest version
        LOGGER.info("Connector {} needs update: {} vs {}", repository, connectorInfo.dockerImageTag, latestImageTag);
        writeOrUpdateStandardDefinition(ctx, configType, latestDefinition);
        updatedCount++;
      } else if (!newFields.isEmpty()) {
        // Add new fields to the connector definition
        final JsonNode definitionToUpdate = getDefinitionWithNewFields(currentDefinition, latestDefinition, newFields);
        LOGGER.info("Connector {} has new fields: {}", repository, String.join(", ", newFields));
        writeOrUpdateStandardDefinition(ctx, configType, definitionToUpdate);
        updatedCount++;
      } else {
        LOGGER.info("Connector {} does not need update: {}", repository, connectorInfo.dockerImageTag);
      }
    }

    return new ConnectorCounter(newCount, updatedCount);
  }

  private void writeOrUpdateStandardDefinition(final DSLContext ctx,
                                               final AirbyteConfig configType,
                                               final JsonNode definition) {
    if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      ConfigWriter.writeStandardSourceDefinition(Collections.singletonList(Jsons.object(definition, StandardSourceDefinition.class)), ctx);
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      ConfigWriter.writeStandardDestinationDefinition(Collections.singletonList(Jsons.object(definition, StandardDestinationDefinition.class)), ctx);
    } else {
      throw new IllegalArgumentException(UNKNOWN_CONFIG_TYPE + configType);
    }
  }

  @VisibleForTesting
  static Set<String> getNewFields(final JsonNode currentDefinition, final JsonNode latestDefinition) {
    final Set<String> currentFields = MoreIterators.toSet(currentDefinition.fieldNames());
    final Set<String> latestFields = MoreIterators.toSet(latestDefinition.fieldNames());
    return Sets.difference(latestFields, currentFields);
  }

  /**
   * @return a clone of the current definition with the new fields from the latest definition.
   */
  @VisibleForTesting
  static JsonNode getDefinitionWithNewFields(final JsonNode currentDefinition, final JsonNode latestDefinition, final Set<String> newFields) {
    final ObjectNode currentClone = (ObjectNode) Jsons.clone(currentDefinition);
    newFields.forEach(field -> currentClone.set(field, latestDefinition.get(field)));
    return currentClone;
  }

  @VisibleForTesting
  static boolean hasNewVersion(final String currentVersion, final String latestVersion) {
    try {
      return new AirbyteVersion(latestVersion).patchVersionCompareTo(new AirbyteVersion(currentVersion)) > 0;
    } catch (final Exception e) {
      LOGGER.error("Failed to check version: {} vs {}", currentVersion, latestVersion);
      return false;
    }
  }

  @VisibleForTesting
  static boolean hasNewPatchVersion(final String currentVersion, final String latestVersion) {
    return new AirbyteVersion(latestVersion).checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion(currentVersion));
  }

  static class ConnectorInfo {

    final String definitionId;
    final JsonNode definition;
    final String dockerRepository;
    final String dockerImageTag;

    ConnectorInfo(final String definitionId, final JsonNode definition) {
      this.definitionId = definitionId;
      this.definition = definition;
      this.dockerRepository = definition.get("dockerRepository").asText();
      this.dockerImageTag = definition.get("dockerImageTag").asText();
    }

    @Override
    public String toString() {
      return String.format("%s: %s (%s)", dockerRepository, dockerImageTag, definitionId);
    }

  }

  private static class ConnectorCounter {

    private final int newCount;
    private final int updateCount;

    private ConnectorCounter(final int newCount, final int updateCount) {
      this.newCount = newCount;
      this.updateCount = updateCount;
    }

  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.CheckOperationRead;
import io.airbyte.api.model.generated.CheckOperationRead.StatusEnum;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationIdRequestBody;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class OperationsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidGenerator;

  @VisibleForTesting
  OperationsHandler(final ConfigRepository configRepository, final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
  }

  public OperationsHandler(final ConfigRepository configRepository) {
    this(configRepository, UUID::randomUUID);
  }

  public CheckOperationRead checkOperation(final OperatorConfiguration operationCheck) {
    try {
      validateOperation(operationCheck);
    } catch (final IllegalArgumentException e) {
      return new CheckOperationRead().status(StatusEnum.FAILED)
          .message(e.getMessage());
    }
    return new CheckOperationRead().status(StatusEnum.SUCCEEDED);
  }

  public OperationRead createOperation(final OperationCreate operationCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID operationId = uuidGenerator.get();
    final StandardSyncOperation standardSyncOperation = toStandardSyncOperation(operationCreate)
        .withOperationId(operationId);
    return persistOperation(standardSyncOperation);
  }

  private static StandardSyncOperation toStandardSyncOperation(final OperationCreate operationCreate) {
    final StandardSyncOperation standardSyncOperation = new StandardSyncOperation()
        .withWorkspaceId(operationCreate.getWorkspaceId())
        .withName(operationCreate.getName())
        .withOperatorType(Enums.convertTo(operationCreate.getOperatorConfiguration().getOperatorType(), OperatorType.class))
        .withTombstone(false);
    if (operationCreate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.generated.OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(operationCreate.getOperatorConfiguration().getNormalization() != null);
      standardSyncOperation.withOperatorNormalization(new OperatorNormalization()
          .withOption(Enums.convertTo(operationCreate.getOperatorConfiguration().getNormalization().getOption(), Option.class)));
    }
    if (operationCreate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.generated.OperatorType.DBT) {
      Preconditions.checkArgument(operationCreate.getOperatorConfiguration().getDbt() != null);
      standardSyncOperation.withOperatorDbt(new OperatorDbt()
          .withGitRepoUrl(operationCreate.getOperatorConfiguration().getDbt().getGitRepoUrl())
          .withGitRepoBranch(operationCreate.getOperatorConfiguration().getDbt().getGitRepoBranch())
          .withDockerImage(operationCreate.getOperatorConfiguration().getDbt().getDockerImage())
          .withDbtArguments(operationCreate.getOperatorConfiguration().getDbt().getDbtArguments()));
    }
    return standardSyncOperation;
  }

  private void validateOperation(final OperatorConfiguration operatorConfiguration) {
    if (operatorConfiguration.getOperatorType() == io.airbyte.api.model.generated.OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(operatorConfiguration.getNormalization() != null);
    }
    if (operatorConfiguration.getOperatorType() == io.airbyte.api.model.generated.OperatorType.DBT) {
      Preconditions.checkArgument(operatorConfiguration.getDbt() != null);
    }
  }

  public OperationRead updateOperation(final OperationUpdate operationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationUpdate.getOperationId());
    return persistOperation(updateOperation(operationUpdate, standardSyncOperation));
  }

  private OperationRead persistOperation(final StandardSyncOperation standardSyncOperation)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardSyncOperation(standardSyncOperation);
    return buildOperationRead(standardSyncOperation.getOperationId());
  }

  public static StandardSyncOperation updateOperation(final OperationUpdate operationUpdate, final StandardSyncOperation standardSyncOperation) {
    standardSyncOperation
        .withName(operationUpdate.getName())
        .withOperatorType(Enums.convertTo(operationUpdate.getOperatorConfiguration().getOperatorType(), OperatorType.class));
    if (operationUpdate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.generated.OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(operationUpdate.getOperatorConfiguration().getNormalization() != null);
      standardSyncOperation.withOperatorNormalization(new OperatorNormalization()
          .withOption(Enums.convertTo(operationUpdate.getOperatorConfiguration().getNormalization().getOption(), Option.class)));
    } else {
      standardSyncOperation.withOperatorNormalization(null);
    }
    if (operationUpdate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.generated.OperatorType.DBT) {
      Preconditions.checkArgument(operationUpdate.getOperatorConfiguration().getDbt() != null);
      standardSyncOperation.withOperatorDbt(new OperatorDbt()
          .withGitRepoUrl(operationUpdate.getOperatorConfiguration().getDbt().getGitRepoUrl())
          .withGitRepoBranch(operationUpdate.getOperatorConfiguration().getDbt().getGitRepoBranch())
          .withDockerImage(operationUpdate.getOperatorConfiguration().getDbt().getDockerImage())
          .withDbtArguments(operationUpdate.getOperatorConfiguration().getDbt().getDbtArguments()));
    } else {
      standardSyncOperation.withOperatorDbt(null);
    }
    return standardSyncOperation;
  }

  public OperationReadList listOperationsForConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<OperationRead> operationReads = Lists.newArrayList();
    final StandardSync standardSync = configRepository.getStandardSync(connectionIdRequestBody.getConnectionId());
    for (final UUID operationId : standardSync.getOperationIds()) {
      final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
      if (standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone()) {
        continue;
      }
      operationReads.add(buildOperationRead(standardSyncOperation));
    }
    return new OperationReadList().operations(operationReads);
  }

  public OperationRead getOperation(final OperationIdRequestBody operationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildOperationRead(operationIdRequestBody.getOperationId());
  }

  public void deleteOperationsForConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionIdRequestBody.getConnectionId());
    deleteOperationsForConnection(standardSync, standardSync.getOperationIds());
  }

  public void deleteOperationsForConnection(final UUID connectionId, final List<UUID> deleteOperationIds)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    deleteOperationsForConnection(standardSync, deleteOperationIds);
  }

  public void deleteOperationsForConnection(final StandardSync standardSync, final List<UUID> deleteOperationIds)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<UUID> operationIds = new ArrayList<>(standardSync.getOperationIds());
    for (final UUID operationId : deleteOperationIds) {
      operationIds.remove(operationId);
      boolean sharedOperation = false;
      for (final StandardSync sync : configRepository.listStandardSyncsUsingOperation(operationId)) {
        // Check if other connections are using the same operation
        if (sync.getConnectionId() != standardSync.getConnectionId()) {
          sharedOperation = true;
          break;
        }
      }
      if (!sharedOperation) {
        removeOperation(operationId);
      }
    }

    configRepository.updateConnectionOperationIds(standardSync.getConnectionId(), new HashSet<>(operationIds));
  }

  public void deleteOperation(final OperationIdRequestBody operationIdRequestBody)
      throws IOException {
    final UUID operationId = operationIdRequestBody.getOperationId();
    configRepository.deleteStandardSyncOperation(operationId);
  }

  private void removeOperation(final UUID operationId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
    if (standardSyncOperation != null) {
      standardSyncOperation.withTombstone(true);
      persistOperation(standardSyncOperation);
    } else {
      throw new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString());
    }
  }

  private OperationRead buildOperationRead(final UUID operationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
    if (standardSyncOperation != null) {
      return buildOperationRead(standardSyncOperation);
    } else {
      throw new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString());
    }
  }

  private static OperationRead buildOperationRead(final StandardSyncOperation standardSyncOperation) {
    final OperatorConfiguration operatorConfiguration = new OperatorConfiguration()
        .operatorType(Enums.convertTo(standardSyncOperation.getOperatorType(), io.airbyte.api.model.generated.OperatorType.class));
    if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(standardSyncOperation.getOperatorNormalization() != null);
      operatorConfiguration.normalization(new io.airbyte.api.model.generated.OperatorNormalization()
          .option(Enums.convertTo(standardSyncOperation.getOperatorNormalization().getOption(), OptionEnum.class)));
    }
    if (standardSyncOperation.getOperatorType() == OperatorType.DBT) {
      Preconditions.checkArgument(standardSyncOperation.getOperatorDbt() != null);
      operatorConfiguration.dbt(new io.airbyte.api.model.generated.OperatorDbt()
          .gitRepoUrl(standardSyncOperation.getOperatorDbt().getGitRepoUrl())
          .gitRepoBranch(standardSyncOperation.getOperatorDbt().getGitRepoBranch())
          .dockerImage(standardSyncOperation.getOperatorDbt().getDockerImage())
          .dbtArguments(standardSyncOperation.getOperatorDbt().getDbtArguments()));
    }
    return new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(operatorConfiguration);
  }

}

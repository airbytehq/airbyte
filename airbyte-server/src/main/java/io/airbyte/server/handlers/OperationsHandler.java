/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.OperationCreate;
import io.airbyte.api.model.OperationIdRequestBody;
import io.airbyte.api.model.OperationRead;
import io.airbyte.api.model.OperationReadList;
import io.airbyte.api.model.OperationUpdate;
import io.airbyte.api.model.OperatorConfiguration;
import io.airbyte.api.model.OperatorNormalization.OptionEnum;
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

  public OperationRead createOperation(OperationCreate operationCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID operationId = uuidGenerator.get();
    final StandardSyncOperation standardSyncOperation = new StandardSyncOperation()
        .withOperationId(operationId)
        .withName(operationCreate.getName())
        .withOperatorType(Enums.convertTo(operationCreate.getOperatorConfiguration().getOperatorType(), OperatorType.class))
        .withTombstone(false);
    if (operationCreate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(operationCreate.getOperatorConfiguration().getNormalization() != null);
      standardSyncOperation.withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC));
    }
    if (operationCreate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.OperatorType.DBT) {
      Preconditions.checkArgument(operationCreate.getOperatorConfiguration().getDbt() != null);
      standardSyncOperation.withOperatorDbt(new OperatorDbt()
          .withGitRepoUrl(operationCreate.getOperatorConfiguration().getDbt().getGitRepoUrl())
          .withDockerImage(operationCreate.getOperatorConfiguration().getDbt().getDockerImage())
          .withDbtArguments(operationCreate.getOperatorConfiguration().getDbt().getDbtArguments()));
    }
    configRepository.writeStandardSyncOperation(standardSyncOperation);
    return buildOperationRead(operationId);
  }

  public OperationRead updateOperation(OperationUpdate operationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSyncOperation persistedSync = configRepository.getStandardSyncOperation(operationUpdate.getOperationId())
        .withName(operationUpdate.getName())
        .withOperatorType(Enums.convertTo(operationUpdate.getOperatorConfiguration().getOperatorType(), OperatorType.class));
    if (operationUpdate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(operationUpdate.getOperatorConfiguration().getNormalization() != null);
      persistedSync.withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC));
    } else {
      persistedSync.withOperatorNormalization(null);
    }
    if (operationUpdate.getOperatorConfiguration().getOperatorType() == io.airbyte.api.model.OperatorType.DBT) {
      Preconditions.checkArgument(operationUpdate.getOperatorConfiguration().getDbt() != null);
      persistedSync.withOperatorDbt(new OperatorDbt()
          .withGitRepoUrl(operationUpdate.getOperatorConfiguration().getDbt().getGitRepoUrl())
          .withDockerImage(operationUpdate.getOperatorConfiguration().getDbt().getDockerImage())
          .withDbtArguments(operationUpdate.getOperatorConfiguration().getDbt().getDbtArguments()));
    } else {
      persistedSync.withOperatorDbt(null);
    }
    return updateOperation(operationUpdate, persistedSync);
  }

  public OperationRead updateOperation(OperationUpdate operationUpdate, StandardSyncOperation persistedSync)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID operationId = operationUpdate.getOperationId();
    configRepository.writeStandardSyncOperation(persistedSync);
    return buildOperationRead(operationId);
  }

  public OperationReadList listOperationsForConnection(ConnectionIdRequestBody connectionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<OperationRead> operationReads = Lists.newArrayList();
    final StandardSync standardSync = configRepository.getStandardSync(connectionIdRequestBody.getConnectionId());
    for (StandardSyncOperation standardSyncOperation : configRepository.listStandardSyncOperations()) {
      if (standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone()) {
        continue;
      }
      if (!standardSync.getOperationIds().contains(standardSyncOperation.getOperationId())) {
        continue;
      }
      operationReads.add(buildOperationRead(standardSyncOperation.getOperationId()));
    }
    return new OperationReadList().operations(operationReads);
  }

  public OperationRead getOperation(OperationIdRequestBody operationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildOperationRead(operationIdRequestBody.getOperationId());
  }

  public void deleteOperation(OperationIdRequestBody operationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID operationId = operationIdRequestBody.getOperationId();
    // Remove operation from all connections using it
    for (StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getOperationIds().removeAll(List.of(operationId))) {
        configRepository.writeStandardSync(standardSync);
      }
    }
    final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
    if (standardSyncOperation != null) {
      standardSyncOperation.withTombstone(true);
      configRepository.writeStandardSyncOperation(standardSyncOperation);
    } else {
      throw new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString());
    }
  }

  private OperationRead buildOperationRead(UUID operationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
    if (standardSyncOperation != null) {
      return buildOperationRead(standardSyncOperation);
    } else {
      throw new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString());
    }
  }

  private OperationRead buildOperationRead(StandardSyncOperation standardSyncOperation) {
    final OperatorConfiguration operatorConfiguration = new OperatorConfiguration()
        .operatorType(Enums.convertTo(standardSyncOperation.getOperatorType(), io.airbyte.api.model.OperatorType.class));
    if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
      Preconditions.checkArgument(standardSyncOperation.getOperatorNormalization() != null);
      operatorConfiguration.normalization(new io.airbyte.api.model.OperatorNormalization()
          .option(Enums.convertTo(standardSyncOperation.getOperatorNormalization().getOption(), OptionEnum.class)));
    }
    if (standardSyncOperation.getOperatorType() == OperatorType.DBT) {
      Preconditions.checkArgument(standardSyncOperation.getOperatorDbt() != null);
      operatorConfiguration.dbt(new io.airbyte.api.model.OperatorDbt()
          .gitRepoUrl(standardSyncOperation.getOperatorDbt().getGitRepoUrl())
          .dockerImage(standardSyncOperation.getOperatorDbt().getDockerImage())
          .dbtArguments(standardSyncOperation.getOperatorDbt().getDbtArguments()));
    }
    return new OperationRead()
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(operatorConfiguration);
  }

}

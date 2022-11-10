/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.OperatorWebhook;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;

public class OperationsConverter {

  public static void populateOperatorConfigFromApi(final OperatorConfiguration operatorConfig, final StandardSyncOperation standardSyncOperation) {
    standardSyncOperation.withOperatorType(Enums.convertTo(operatorConfig.getOperatorType(), OperatorType.class));
    switch (operatorConfig.getOperatorType()) {
      case NORMALIZATION -> {
        Preconditions.checkArgument(operatorConfig.getNormalization() != null);
        standardSyncOperation.withOperatorNormalization(new OperatorNormalization()
            .withOption(Enums.convertTo(operatorConfig.getNormalization().getOption(), Option.class)));
        // Null out the other configs, since it's mutually exclusive. We need to do this if it's an update.
        standardSyncOperation.withOperatorDbt(null);
        standardSyncOperation.withOperatorWebhook(null);
      }
      case DBT -> {
        Preconditions.checkArgument(operatorConfig.getDbt() != null);
        standardSyncOperation.withOperatorDbt(new OperatorDbt()
            .withGitRepoUrl(operatorConfig.getDbt().getGitRepoUrl())
            .withGitRepoBranch(operatorConfig.getDbt().getGitRepoBranch())
            .withDockerImage(operatorConfig.getDbt().getDockerImage())
            .withDbtArguments(operatorConfig.getDbt().getDbtArguments()));
        // Null out the other configs, since they're mutually exclusive. We need to do this if it's an
        // update.
        standardSyncOperation.withOperatorNormalization(null);
        standardSyncOperation.withOperatorWebhook(null);
      }
      case WEBHOOK -> {
        Preconditions.checkArgument(operatorConfig.getWebhook() != null);
        // TODO(mfsiega-airbyte): check that the webhook config id references a real webhook config.
        standardSyncOperation.withOperatorWebhook(new OperatorWebhook()
            .withExecutionUrl(operatorConfig.getWebhook().getExecutionUrl())
            .withExecutionBody(operatorConfig.getWebhook().getExecutionBody())
            .withWebhookConfigId(operatorConfig.getWebhook().getWebhookConfigId()));
        // Null out the other configs, since it's mutually exclusive. We need to do this if it's an update.
        standardSyncOperation.withOperatorNormalization(null);
        standardSyncOperation.withOperatorDbt(null);
      }
    }
  }

  public static OperationRead operationReadFromPersistedOperation(final StandardSyncOperation standardSyncOperation) {
    final OperatorConfiguration operatorConfiguration = new OperatorConfiguration()
        .operatorType(Enums.convertTo(standardSyncOperation.getOperatorType(), io.airbyte.api.model.generated.OperatorType.class));
    if (standardSyncOperation.getOperatorType() == null) {
      // TODO(mfsiega-airbyte): this case shouldn't happen, but the API today would tolerate it. After
      // verifying that it really can't happen, turn this into a precondition.
      return new OperationRead()
          .workspaceId(standardSyncOperation.getWorkspaceId())
          .operationId(standardSyncOperation.getOperationId())
          .name(standardSyncOperation.getName());
    }
    switch (standardSyncOperation.getOperatorType()) {
      case NORMALIZATION -> {
        Preconditions.checkArgument(standardSyncOperation.getOperatorNormalization() != null);
        operatorConfiguration.normalization(new io.airbyte.api.model.generated.OperatorNormalization()
            .option(Enums.convertTo(standardSyncOperation.getOperatorNormalization().getOption(), OptionEnum.class)));
      }
      case DBT -> {
        Preconditions.checkArgument(standardSyncOperation.getOperatorDbt() != null);
        operatorConfiguration.dbt(new io.airbyte.api.model.generated.OperatorDbt()
            .gitRepoUrl(standardSyncOperation.getOperatorDbt().getGitRepoUrl())
            .gitRepoBranch(standardSyncOperation.getOperatorDbt().getGitRepoBranch())
            .dockerImage(standardSyncOperation.getOperatorDbt().getDockerImage())
            .dbtArguments(standardSyncOperation.getOperatorDbt().getDbtArguments()));
      }
      case WEBHOOK -> {
        Preconditions.checkArgument(standardSyncOperation.getOperatorWebhook() != null);
        operatorConfiguration.webhook(new io.airbyte.api.model.generated.OperatorWebhook()
            .webhookConfigId(standardSyncOperation.getOperatorWebhook().getWebhookConfigId())
            .executionUrl(standardSyncOperation.getOperatorWebhook().getExecutionUrl())
            .executionBody(standardSyncOperation.getOperatorWebhook().getExecutionBody()));
      }
    }
    return new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(operatorConfiguration);
  }

}

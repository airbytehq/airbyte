/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static io.airbyte.api.model.generated.OperatorWebhook.WebhookTypeEnum.DBTCLOUD;
import static io.airbyte.api.model.generated.OperatorWebhook.WebhookTypeEnum.GENERIC;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.api.model.generated.OperatorWebhookDbtCloud;
import io.airbyte.api.model.generated.OperatorWebhookGeneric;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.OperatorWebhook;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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
        standardSyncOperation.withOperatorWebhook(webhookOperatorFromConfig(operatorConfig.getWebhook()));
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
        operatorConfiguration.webhook(webhookOperatorFromPersistence(standardSyncOperation.getOperatorWebhook()));
      }
    }
    return new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(operatorConfiguration);
  }

  private static OperatorWebhook webhookOperatorFromConfig(io.airbyte.api.model.generated.OperatorWebhook webhookConfig) {
    final var operatorWebhook = new OperatorWebhook().withWebhookConfigId(webhookConfig.getWebhookConfigId());
    if (webhookConfig.getWebhookType() == null) {
      return operatorWebhook
          .withExecutionUrl(webhookConfig.getExecutionUrl())
          .withExecutionBody(webhookConfig.getExecutionBody());
    }
    switch (webhookConfig.getWebhookType()) {
      case DBTCLOUD -> {
        return operatorWebhook
            .withExecutionUrl(String.format("https://cloud.getdbt.com/api/v2/accounts/%d/jobs/%d/run/", webhookConfig.getDbtCloud().getAccountId(),
                webhookConfig.getDbtCloud().getJobId()))
            .withExecutionBody("{\"cause\": \"airbyte\"}");
      }
      case GENERIC -> {
        return operatorWebhook
            .withExecutionUrl(webhookConfig.getGeneric().getExecutionUrl())
            .withExecutionBody(webhookConfig.getGeneric().getExecutionBody());
      }
    }
    throw new IllegalArgumentException("Unsupported webhook operation type");
  }

  private static io.airbyte.api.model.generated.OperatorWebhook webhookOperatorFromPersistence(final OperatorWebhook persistedWebhook) {
    final io.airbyte.api.model.generated.OperatorWebhook webhookOperator = new io.airbyte.api.model.generated.OperatorWebhook()
        .webhookConfigId(persistedWebhook.getWebhookConfigId());
    OperatorWebhookDbtCloud dbtCloudOperator = DbtCloudOperationConverter.parseFrom(persistedWebhook);
    if (dbtCloudOperator != null) {
      webhookOperator.webhookType(DBTCLOUD).dbtCloud(DbtCloudOperationConverter.parseFrom(persistedWebhook));
    } else {
      webhookOperator.webhookType(GENERIC).generic(new OperatorWebhookGeneric()
          .executionBody(persistedWebhook.getExecutionBody())
          .executionUrl(persistedWebhook.getExecutionUrl()));
      // NOTE: double-write until the frontend starts using the new fields.
      webhookOperator.executionUrl(persistedWebhook.getExecutionUrl()).executionBody(persistedWebhook.getExecutionBody());
    }
    return webhookOperator;
  }

  private static class DbtCloudOperationConverter {

    final static Pattern dbtUrlPattern = Pattern.compile("^https://cloud\\.getdbt\\.com/api/v2/accounts/(\\d+)/jobs/(\\d+)/run/$");
    private static final int ACCOUNT_REGEX_GROUP = 1;
    private static final int JOB_REGEX_GROUP = 2;

    private static OperatorWebhookDbtCloud parseFrom(OperatorWebhook persistedWebhook) {
      Matcher dbtCloudUrlMatcher = dbtUrlPattern.matcher(persistedWebhook.getExecutionUrl());
      final var dbtCloudConfig = new OperatorWebhookDbtCloud();
      if (dbtCloudUrlMatcher.matches()) {
        dbtCloudConfig.setAccountId(Integer.valueOf(dbtCloudUrlMatcher.group(ACCOUNT_REGEX_GROUP)));
        dbtCloudConfig.setJobId(Integer.valueOf(dbtCloudUrlMatcher.group(JOB_REGEX_GROUP)));
        return dbtCloudConfig;
      }
      return null;
    }

  }

}

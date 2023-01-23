/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import static io.airbyte.api.model.generated.OperatorWebhook.WebhookTypeEnum.DBTCLOUD;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.api.model.generated.OperatorWebhookDbtCloud;
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
    // TODO(mfsiega-airbyte): remove this once the frontend is sending the new format.
    if (webhookConfig.getWebhookType() == null) {
      return operatorWebhook
          .withExecutionUrl(webhookConfig.getExecutionUrl())
          .withExecutionBody(webhookConfig.getExecutionBody());
    }
    switch (webhookConfig.getWebhookType()) {
      case DBTCLOUD -> {
        return operatorWebhook
            .withExecutionUrl(DbtCloudOperationConverter.getExecutionUrlFrom(webhookConfig.getDbtCloud()))
            .withExecutionBody(DbtCloudOperationConverter.getDbtCloudExecutionBody());
      }
      // Future webhook operator types added here.
    }
    throw new IllegalArgumentException("Unsupported webhook operation type");
  }

  private static io.airbyte.api.model.generated.OperatorWebhook webhookOperatorFromPersistence(final OperatorWebhook persistedWebhook) {
    final io.airbyte.api.model.generated.OperatorWebhook webhookOperator = new io.airbyte.api.model.generated.OperatorWebhook()
        .webhookConfigId(persistedWebhook.getWebhookConfigId());
    OperatorWebhookDbtCloud dbtCloudOperator = DbtCloudOperationConverter.parseFrom(persistedWebhook);
    if (dbtCloudOperator != null) {
      webhookOperator.webhookType(DBTCLOUD).dbtCloud(dbtCloudOperator);
      // TODO(mfsiega-airbyte): remove once frontend switches to new format.
      // Dual-write deprecated webhook format.
      webhookOperator.executionUrl(DbtCloudOperationConverter.getExecutionUrlFrom(dbtCloudOperator));
      webhookOperator.executionBody(DbtCloudOperationConverter.getDbtCloudExecutionBody());
    } else {
      throw new IllegalArgumentException("Unexpected webhook operator config");
    }
    return webhookOperator;
  }

  private static class DbtCloudOperationConverter {

    // See https://docs.getdbt.com/dbt-cloud/api-v2 for documentation on dbt Cloud API endpoints.
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

    private static String getExecutionUrlFrom(final OperatorWebhookDbtCloud dbtCloudConfig) {
      return String.format("https://cloud.getdbt.com/api/v2/accounts/%d/jobs/%d/run/", dbtCloudConfig.getAccountId(),
          dbtCloudConfig.getJobId());
    }

    private static String getDbtCloudExecutionBody() {
      return "{\"cause\": \"airbyte\"}";
    }

  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationIdRequestBody;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.OperatorDbt;
import io.airbyte.api.model.generated.OperatorNormalization;
import io.airbyte.api.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.api.model.generated.OperatorType;
import io.airbyte.api.model.generated.OperatorWebhook;
import io.airbyte.api.model.generated.OperatorWebhook.WebhookTypeEnum;
import io.airbyte.api.model.generated.OperatorWebhookDbtCloud;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OperationsHandlerTest {

  private static final String WEBHOOK_OPERATION_NAME = "fake-operation-name";
  private static final UUID WEBHOOK_CONFIG_ID = UUID.randomUUID();
  private static final UUID WEBHOOK_OPERATION_ID = UUID.randomUUID();
  private static final Integer DBT_CLOUD_WEBHOOK_ACCOUNT_ID = 123;
  private static final Integer DBT_CLOUD_WEBHOOK_JOB_ID = 456;
  private static final Integer NEW_DBT_CLOUD_WEBHOOK_ACCOUNT_ID = 789;
  public static final String EXECUTION_BODY = "{\"cause\": \"airbyte\"}";
  public static final String EXECUTION_URL_TEMPLATE = "https://cloud.getdbt.com/api/v2/accounts/%d/jobs/%d/run/";
  private ConfigRepository configRepository;
  private Supplier<UUID> uuidGenerator;
  private OperationsHandler operationsHandler;
  private StandardSyncOperation standardSyncOperation;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    uuidGenerator = mock(Supplier.class);

    operationsHandler = new OperationsHandler(configRepository, uuidGenerator);
    standardSyncOperation = new StandardSyncOperation()
        .withWorkspaceId(UUID.randomUUID())
        .withOperationId(UUID.randomUUID())
        .withName("presto to hudi")
        .withOperatorType(io.airbyte.config.StandardSyncOperation.OperatorType.NORMALIZATION)
        .withOperatorNormalization(new io.airbyte.config.OperatorNormalization().withOption(Option.BASIC))
        .withOperatorDbt(null)
        .withTombstone(false);
  }

  @Test
  void testCreateOperation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(standardSyncOperation.getOperationId());

    when(configRepository.getStandardSyncOperation(standardSyncOperation.getOperationId())).thenReturn(standardSyncOperation);

    final OperationCreate operationCreate = new OperationCreate()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.NORMALIZATION)
            .normalization(new OperatorNormalization().option(OptionEnum.BASIC)));

    final OperationRead actualOperationRead = operationsHandler.createOperation(operationCreate);

    final OperationRead expectedOperationRead = new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.NORMALIZATION)
            .normalization(new OperatorNormalization().option(OptionEnum.BASIC)));

    assertEquals(expectedOperationRead, actualOperationRead);

    verify(configRepository).writeStandardSyncOperation(standardSyncOperation);
  }

  @Test
  void testCreateWebhookOperation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(WEBHOOK_OPERATION_ID);
    final OperatorWebhook webhookConfig = new OperatorWebhook()
        .webhookConfigId(WEBHOOK_CONFIG_ID)
        .webhookType(WebhookTypeEnum.DBTCLOUD)
        .dbtCloud(new OperatorWebhookDbtCloud()
            .accountId(DBT_CLOUD_WEBHOOK_ACCOUNT_ID)
            .jobId(DBT_CLOUD_WEBHOOK_JOB_ID));
    final OperationCreate operationCreate = new OperationCreate()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .name(WEBHOOK_OPERATION_NAME)
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.WEBHOOK).webhook(webhookConfig));

    final StandardSyncOperation expectedPersistedOperation = new StandardSyncOperation()
        .withWorkspaceId(standardSyncOperation.getWorkspaceId())
        .withOperationId(WEBHOOK_OPERATION_ID)
        .withName(WEBHOOK_OPERATION_NAME)
        .withOperatorType(StandardSyncOperation.OperatorType.WEBHOOK)
        .withOperatorWebhook(new io.airbyte.config.OperatorWebhook()
            .withWebhookConfigId(WEBHOOK_CONFIG_ID)
            .withExecutionUrl(String.format(EXECUTION_URL_TEMPLATE, DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
                DBT_CLOUD_WEBHOOK_JOB_ID))
            .withExecutionBody(EXECUTION_BODY))
        .withTombstone(false);

    when(configRepository.getStandardSyncOperation(WEBHOOK_OPERATION_ID)).thenReturn(expectedPersistedOperation);

    final OperationRead actualOperationRead = operationsHandler.createOperation(operationCreate);

    assertEquals(operationCreate.getWorkspaceId(), actualOperationRead.getWorkspaceId());
    assertEquals(WEBHOOK_OPERATION_ID, actualOperationRead.getOperationId());
    assertEquals(WEBHOOK_OPERATION_NAME, actualOperationRead.getName());
    assertEquals(OperatorType.WEBHOOK, actualOperationRead.getOperatorConfiguration().getOperatorType());

    // NOTE: we expect the server to dual-write on read until the frontend moves to the new format.
    final OperatorWebhook expectedWebhookConfigRead =
        webhookConfig.executionUrl(String.format(EXECUTION_URL_TEMPLATE, DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID)).executionBody(EXECUTION_BODY);
    assertEquals(expectedWebhookConfigRead, actualOperationRead.getOperatorConfiguration().getWebhook());

    verify(configRepository).writeStandardSyncOperation(eq(expectedPersistedOperation));
  }

  @Test
  void testUpdateOperation() throws JsonValidationException, ConfigNotFoundException, IOException {
    final OperationUpdate operationUpdate = new OperationUpdate()
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.DBT)
            .dbt(new OperatorDbt()
                .gitRepoUrl("git_repo_url")
                .gitRepoBranch("git_repo_branch")
                .dockerImage("docker")
                .dbtArguments("--full-refresh")));

    final StandardSyncOperation updatedStandardSyncOperation = new StandardSyncOperation()
        .withWorkspaceId(standardSyncOperation.getWorkspaceId())
        .withOperationId(standardSyncOperation.getOperationId())
        .withName(standardSyncOperation.getName())
        .withOperatorType(io.airbyte.config.StandardSyncOperation.OperatorType.DBT)
        .withOperatorDbt(new io.airbyte.config.OperatorDbt()
            .withGitRepoUrl("git_repo_url")
            .withGitRepoBranch("git_repo_branch")
            .withDockerImage("docker")
            .withDbtArguments("--full-refresh"))
        .withOperatorNormalization(null)
        .withTombstone(false);

    when(configRepository.getStandardSyncOperation(standardSyncOperation.getOperationId())).thenReturn(standardSyncOperation)
        .thenReturn(updatedStandardSyncOperation);

    final OperationRead actualOperationRead = operationsHandler.updateOperation(operationUpdate);

    final OperationRead expectedOperationRead = new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.DBT)
            .dbt(new OperatorDbt()
                .gitRepoUrl("git_repo_url")
                .gitRepoBranch("git_repo_branch")
                .dockerImage("docker")
                .dbtArguments("--full-refresh")));

    assertEquals(expectedOperationRead, actualOperationRead);

    verify(configRepository).writeStandardSyncOperation(updatedStandardSyncOperation);
  }

  @Test
  void testUpdateWebhookOperation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(WEBHOOK_OPERATION_ID);
    final OperatorWebhook webhookConfig = new OperatorWebhook()
        .webhookConfigId(WEBHOOK_CONFIG_ID)
        .webhookType(WebhookTypeEnum.DBTCLOUD)
        .dbtCloud(new OperatorWebhookDbtCloud()
            .accountId(NEW_DBT_CLOUD_WEBHOOK_ACCOUNT_ID)
            .jobId(DBT_CLOUD_WEBHOOK_JOB_ID));
    final OperationUpdate operationUpdate = new OperationUpdate()
        .name(WEBHOOK_OPERATION_NAME)
        .operationId(WEBHOOK_OPERATION_ID)
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.WEBHOOK).webhook(webhookConfig));

    final var persistedWebhook = new io.airbyte.config.OperatorWebhook()
        .withWebhookConfigId(WEBHOOK_CONFIG_ID)
        .withExecutionUrl(String.format(EXECUTION_URL_TEMPLATE, DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID))
        .withExecutionBody(EXECUTION_BODY);

    final var updatedWebhook = new io.airbyte.config.OperatorWebhook()
        .withWebhookConfigId(WEBHOOK_CONFIG_ID)
        .withExecutionUrl(String.format(EXECUTION_URL_TEMPLATE, NEW_DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID))
        .withExecutionBody(EXECUTION_BODY);

    final StandardSyncOperation persistedOperation = new StandardSyncOperation()
        .withWorkspaceId(standardSyncOperation.getWorkspaceId())
        .withOperationId(WEBHOOK_OPERATION_ID)
        .withName(WEBHOOK_OPERATION_NAME)
        .withOperatorType(StandardSyncOperation.OperatorType.WEBHOOK)
        .withOperatorWebhook(persistedWebhook);

    final StandardSyncOperation updatedOperation = new StandardSyncOperation()
        .withWorkspaceId(standardSyncOperation.getWorkspaceId())
        .withOperationId(WEBHOOK_OPERATION_ID)
        .withName(WEBHOOK_OPERATION_NAME)
        .withOperatorType(StandardSyncOperation.OperatorType.WEBHOOK)
        .withOperatorWebhook(updatedWebhook);

    when(configRepository.getStandardSyncOperation(WEBHOOK_OPERATION_ID)).thenReturn(persistedOperation).thenReturn(updatedOperation);

    final OperationRead actualOperationRead = operationsHandler.updateOperation(operationUpdate);

    assertEquals(WEBHOOK_OPERATION_ID, actualOperationRead.getOperationId());
    assertEquals(WEBHOOK_OPERATION_NAME, actualOperationRead.getName());
    assertEquals(OperatorType.WEBHOOK, actualOperationRead.getOperatorConfiguration().getOperatorType());
    final OperatorWebhook expectedWebhookConfigRead =
        webhookConfig.executionUrl(String.format(EXECUTION_URL_TEMPLATE, NEW_DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID)).executionBody(EXECUTION_BODY);
    assertEquals(expectedWebhookConfigRead, actualOperationRead.getOperatorConfiguration().getWebhook());

    verify(configRepository)
        .writeStandardSyncOperation(persistedOperation.withOperatorWebhook(persistedOperation.getOperatorWebhook().withExecutionUrl(
            String.format(EXECUTION_URL_TEMPLATE, NEW_DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
                DBT_CLOUD_WEBHOOK_JOB_ID))));
  }

  @Test
  void testGetOperation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardSyncOperation(standardSyncOperation.getOperationId())).thenReturn(standardSyncOperation);

    final OperationIdRequestBody operationIdRequestBody = new OperationIdRequestBody().operationId(standardSyncOperation.getOperationId());
    final OperationRead actualOperationRead = operationsHandler.getOperation(operationIdRequestBody);

    final OperationRead expectedOperationRead = generateOperationRead();

    assertEquals(expectedOperationRead, actualOperationRead);
  }

  private OperationRead generateOperationRead() {
    return new OperationRead()
        .workspaceId(standardSyncOperation.getWorkspaceId())
        .operationId(standardSyncOperation.getOperationId())
        .name(standardSyncOperation.getName())
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.NORMALIZATION)
            .normalization(new OperatorNormalization().option(OptionEnum.BASIC)));
  }

  @Test
  void testListOperationsForConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID connectionId = UUID.randomUUID();

    when(configRepository.getStandardSync(connectionId))
        .thenReturn(new StandardSync()
            .withOperationIds(List.of(standardSyncOperation.getOperationId())));

    when(configRepository.getStandardSyncOperation(standardSyncOperation.getOperationId()))
        .thenReturn(standardSyncOperation);

    when(configRepository.listStandardSyncOperations())
        .thenReturn(List.of(standardSyncOperation));

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionId);
    final OperationReadList actualOperationReadList = operationsHandler.listOperationsForConnection(connectionIdRequestBody);

    assertEquals(generateOperationRead(), actualOperationReadList.getOperations().get(0));
  }

  @Test
  void testDeleteOperation() throws IOException {
    final OperationIdRequestBody operationIdRequestBody = new OperationIdRequestBody().operationId(standardSyncOperation.getOperationId());

    final OperationsHandler spiedOperationsHandler = spy(operationsHandler);

    spiedOperationsHandler.deleteOperation(operationIdRequestBody);

    verify(configRepository).deleteStandardSyncOperation(standardSyncOperation.getOperationId());
  }

  @Test
  void testDeleteOperationsForConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID syncConnectionId = UUID.randomUUID();
    final UUID otherConnectionId = UUID.randomUUID();
    final UUID operationId = UUID.randomUUID();
    final UUID remainingOperationId = UUID.randomUUID();
    final List<UUID> toDelete = Stream.of(standardSyncOperation.getOperationId(), operationId).collect(Collectors.toList());
    final StandardSync sync = new StandardSync()
        .withConnectionId(syncConnectionId)
        .withOperationIds(List.of(standardSyncOperation.getOperationId(), operationId, remainingOperationId));
    when(configRepository.listStandardSyncs()).thenReturn(List.of(
        sync,
        new StandardSync()
            .withConnectionId(otherConnectionId)
            .withOperationIds(List.of(standardSyncOperation.getOperationId()))));
    final StandardSyncOperation operation = new StandardSyncOperation().withOperationId(operationId);
    final StandardSyncOperation remainingOperation = new StandardSyncOperation().withOperationId(remainingOperationId);
    when(configRepository.getStandardSyncOperation(operationId)).thenReturn(operation);
    when(configRepository.getStandardSyncOperation(remainingOperationId)).thenReturn(remainingOperation);
    when(configRepository.getStandardSyncOperation(standardSyncOperation.getOperationId())).thenReturn(standardSyncOperation);

    // first, test that a remaining operation results in proper call
    operationsHandler.deleteOperationsForConnection(sync, toDelete);
    verify(configRepository).writeStandardSyncOperation(operation.withTombstone(true));
    verify(configRepository).updateConnectionOperationIds(syncConnectionId, Collections.singleton(remainingOperationId));

    // next, test that removing all operations results in proper call
    toDelete.add(remainingOperationId);
    operationsHandler.deleteOperationsForConnection(sync, toDelete);
    verify(configRepository).updateConnectionOperationIds(syncConnectionId, Collections.emptySet());
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.generated.OperatorType.class, io.airbyte.config.StandardSyncOperation.OperatorType.class));
    assertTrue(Enums.isCompatible(io.airbyte.api.model.generated.OperatorNormalization.OptionEnum.class,
        io.airbyte.config.OperatorNormalization.Option.class));
  }

  @Test
  void testDbtCloudRegex() {
    // Validate that a non-url is rejected.
    assertThrows(IllegalArgumentException.class, () -> checkDbtCloudUrl("not-a-url"));
    // Validate that the URL is anchored to the beginning.
    assertThrows(IllegalArgumentException.class,
        () -> checkDbtCloudUrl("some-nonsense-" + String.format(EXECUTION_URL_TEMPLATE, DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID)));
    // Validate that the URL is anchored to the end.
    assertThrows(IllegalArgumentException.class,
        () -> checkDbtCloudUrl(String.format(EXECUTION_URL_TEMPLATE, DBT_CLOUD_WEBHOOK_ACCOUNT_ID,
            DBT_CLOUD_WEBHOOK_JOB_ID) + "-some-nonsense"));
    // Validate that the account id must be an integer.
    assertThrows(IllegalArgumentException.class, () -> checkDbtCloudUrl("https://cloud.getdbt.com/api/v2/accounts/abc/jobs/123/run/"));
    // Validate that the job id must be an integer.
    assertThrows(IllegalArgumentException.class, () -> checkDbtCloudUrl("https://cloud.getdbt.com/api/v2/accounts/123/jobs/abc/run/"));
  }

  private void checkDbtCloudUrl(final String urlToCheck) throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSyncOperation persistedOperation = new StandardSyncOperation()
        .withWorkspaceId(standardSyncOperation.getWorkspaceId())
        .withOperationId(WEBHOOK_OPERATION_ID)
        .withName(WEBHOOK_OPERATION_NAME)
        .withOperatorType(StandardSyncOperation.OperatorType.WEBHOOK)
        .withOperatorWebhook(new io.airbyte.config.OperatorWebhook()
            .withWebhookConfigId(WEBHOOK_CONFIG_ID)
            .withExecutionUrl(urlToCheck)
            .withExecutionBody(EXECUTION_BODY))
        .withTombstone(false);
    when(configRepository.getStandardSyncOperation(WEBHOOK_OPERATION_ID)).thenReturn(persistedOperation);

    final OperationIdRequestBody operationIdRequestBody = new OperationIdRequestBody().operationId(WEBHOOK_OPERATION_ID);
    operationsHandler.getOperation(operationIdRequestBody);
  }

}

/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.temporal.serviceclient.CheckedExceptionWrapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Consumer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.stubbing.Answer;
import org.testcontainers.containers.PostgreSQLContainer;

class TemporalAttemptExecutionTest {

  private static final String JOB_ID = "11";
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig().withJobId(JOB_ID).withAttemptId((long) ATTEMPT_ID);
  private static final String SOURCE_USERNAME = "sourceusername";
  private static final String SOURCE_PASSWORD = "hunter2";

  private static PostgreSQLContainer<?> container;
  private static Configs configs;

  private Path jobRoot;

  private CheckedSupplier<Worker<String, String>, Exception> execution;
  private Consumer<Path> mdcSetter;

  private TemporalAttemptExecution<String, String> attemptExecution;

  @BeforeAll
  static void setUpAll() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withUsername(SOURCE_USERNAME)
        .withPassword(SOURCE_PASSWORD);
    container.start();
    configs = mock(Configs.class);
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(configs.getDatabaseUser()).thenReturn(SOURCE_USERNAME);
    when(configs.getDatabasePassword()).thenReturn(SOURCE_PASSWORD);
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(container);
    databaseProviders.createNewJobsDatabase();

    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_attempt_execution_test");
    jobRoot = workspaceRoot.resolve(JOB_ID).resolve(String.valueOf(ATTEMPT_ID));

    execution = mock(CheckedSupplier.class);
    mdcSetter = mock(Consumer.class);

    attemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        configs.getWorkerEnvironment(), configs.getLogConfigs(),
        JOB_RUN_CONFIG, execution,
        () -> "",
        mdcSetter,
        mock(CancellationHandler.class),
        SOURCE_USERNAME,
        SOURCE_PASSWORD,
        container.getJdbcUrl(),
        () -> "workflow_id", configs.getAirbyteVersionOrWarning());
  }

  @AfterAll
  static void tearDownAll() {
    container.close();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSuccessfulSupplierRun() throws Exception {
    final String expected = "louis XVI";
    final Worker<String, String> worker = mock(Worker.class);
    when(worker.run(any(), any())).thenReturn(expected);

    when(execution.get()).thenAnswer((Answer<Worker<String, String>>) invocation -> worker);

    final String actual = attemptExecution.get();

    assertEquals(expected, actual);

    verify(execution).get();
    verify(mdcSetter, atLeast(2)).accept(jobRoot);
  }

  @Test
  void testThrowsCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IOException());

    final CheckedExceptionWrapper actualException = assertThrows(CheckedExceptionWrapper.class, () -> attemptExecution.get());
    assertEquals(IOException.class, CheckedExceptionWrapper.unwrap(actualException).getClass());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot);
  }

  @Test
  void testThrowsUnCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IllegalArgumentException());

    assertThrows(IllegalArgumentException.class, () -> attemptExecution.get());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot);
  }

}

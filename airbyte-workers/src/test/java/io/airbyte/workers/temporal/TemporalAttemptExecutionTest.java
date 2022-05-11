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
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.workers.Worker;
import io.temporal.serviceclient.CheckedExceptionWrapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
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
  private static DataSource dataSource;
  private static DSLContext dslContext;

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

    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(dataSource, dslContext);
    final Database jobDatabase = databaseProviders.createNewJobsDatabase();
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);

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
        jobPersistence,
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

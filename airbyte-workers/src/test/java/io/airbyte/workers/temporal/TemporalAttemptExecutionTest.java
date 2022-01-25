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
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.RetryOptions;
import io.temporal.serviceclient.CheckedExceptionWrapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Consumer;

import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
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

  private static Path workspaceRoot;
  private Path jobRoot;

  private CheckedSupplier<Worker<String, String>, Exception> execution;
  private static Consumer<Path> mdcSetter;

  private TestWorkflowEnvironment testEnv;
  private io.temporal.worker.Worker worker;
  private WorkflowClient client;
  private TaeTestWorkflow workflow;

  public record Output(String string, Exception e) {}

  @WorkflowInterface
  public interface TaeTestWorkflow {
    @WorkflowMethod
    String run();
  }

  @ActivityInterface
  public interface TaeTestActivity {
    @ActivityMethod
    Output run();
  }

  public class TaeTestActivityImpl implements TaeTestActivity {
    @Override
    public Output run() {
      try {
        return new Output(execution.get().run("", jobRoot), null);
      } catch (final Exception e) {
        return new Output(null, e);
      }
    }
  }

  public static class TaeTestWorkflowImpl implements TaeTestWorkflow {

    private final TaeTestActivity taeTestActivity = Workflow.newActivityStub(TaeTestActivity.class, ActivityConfiguration.OPTIONS);

    @Override
    public String run() {
      final var output =  new TemporalAttemptExecution<>(
              workspaceRoot,
              configs.getWorkerEnvironment(), configs.getLogConfigs(),
              JOB_RUN_CONFIG,
              () -> new Worker<String, Output>() {
                @Override
                public Output run(String s, Path jobRoot) {
                  return taeTestActivity.run();
                }

                @Override
                public void cancel() {
                  // todo: no-op
                }
              },
              () -> "",
              mdcSetter,
              mock(CancellationHandler.class),
              SOURCE_USERNAME,
              SOURCE_PASSWORD,
              container.getJdbcUrl(),
              () -> "workflow_id", configs.getAirbyteVersionOrWarning()).get();

      if(output.string != null) {
        return output.string;
      } else {
        throw Workflow.wrap(output.e);
      }
    }
  }


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
    // configure temporal
    testEnv = TestWorkflowEnvironment.newInstance();
    worker = testEnv.newWorker("queue");
    worker.registerWorkflowImplementationTypes(TaeTestWorkflowImpl.class);
    client = testEnv.getWorkflowClient();
    worker.registerActivitiesImplementations(new TaeTestActivityImpl());
    testEnv.start();
    workflow = client.newWorkflowStub(TaeTestWorkflow.class, WorkflowOptions.newBuilder().setRetryOptions(TemporalUtils.NO_RETRY).setTaskQueue("queue").build());

    // configure the rest
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(container);
    databaseProviders.createNewJobsDatabase();

    workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_attempt_execution_test");
    jobRoot = workspaceRoot.resolve(JOB_ID).resolve(String.valueOf(ATTEMPT_ID));

    execution = mock(CheckedSupplier.class);
    mdcSetter = mock(Consumer.class);
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

    final String actual = workflow.run();

    assertEquals(expected, actual);

    verify(execution).get();
    verify(mdcSetter, atLeast(2)).accept(jobRoot);
  }

  @Test
  void testThrowsCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IOException());

    final CheckedExceptionWrapper actualException = assertThrows(CheckedExceptionWrapper.class, () -> workflow.run());
    assertEquals(IOException.class, CheckedExceptionWrapper.unwrap(actualException).getClass());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot);
  }

  @Test
  void testThrowsUnCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IllegalArgumentException());

    assertThrows(IllegalArgumentException.class, () -> workflow.run());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot);
  }

}

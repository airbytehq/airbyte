package io.dataline.workers.singer;

import static io.dataline.workers.WorkerStatus.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.Worker;
import java.io.IOException;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

// TODO once singer env PR is merged in
public class TestBaseSingerWorker extends BaseWorkerTestCase {

  @Test
  public void testWorkerCancelsSuccessfully() {
    Worker<Object> worker =
        createMockSingerWorker(
            () -> {
              try {
                return Runtime.getRuntime().exec("/bin/bash -c sleep 20");
              } catch (IOException e) {
                throw new RuntimeException(e);
              }
            },
            () -> null);
    new Thread(worker::run).start();

    try {
      TimeUnit.MILLISECONDS.sleep(50);
      worker.cancel();
      TimeUnit.SECONDS.sleep(1);
      assertEquals(CANCELLED, worker.getStatus());
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  public void testSuccessfulWorkerWithZeroExit() {
    String someOutput = "hi";
    Worker<String> worker =
        createMockSingerWorker(
            () -> {
              try {
                Process exec = Runtime.getRuntime().exec("/bin/bash -c exit 0");
                return exec;
              } catch (IOException e) {
                throw new RuntimeException(e);
              }
            },
            () -> someOutput);

    assertEquals(NOT_STARTED, worker.getStatus());
    worker.run();
    assertEquals(COMPLETED, worker.getStatus());
    assertEquals(someOutput, worker.getOutput());
  }

  @Test
  public void testSuccessfulWorkerWithNonZeroExit() {
    String someOutput = "hi";
    Worker<String> worker =
        createMockSingerWorker(
            () -> {
              try {
                Process exec = Runtime.getRuntime().exec("/bin/bash -c exit 1");
                return exec;
              } catch (IOException e) {
                throw new RuntimeException(e);
              }
            },
            () -> someOutput);

    assertEquals(NOT_STARTED, worker.getStatus());
    worker.run();
    assertEquals(COMPLETED, worker.getStatus());
    assertEquals(someOutput, worker.getOutput());
  }

  @Test
  public void testFailedWorker() {
    RuntimeException expected = new RuntimeException("Failure is the predecessor of success");

    Worker<Object> baseSingerWorker =
        createMockSingerWorker(
            () -> {
              throw expected;
            },
            () -> null);

    assertEquals(NOT_STARTED, baseSingerWorker.getStatus());
    try {
      baseSingerWorker.run();
      fail();
    } catch (Exception actual) {
      assertEquals(FAILED, baseSingerWorker.getStatus());
      assertEquals(new RuntimeException(expected).getMessage(), actual.getMessage());
    }
  }

  private <T> Worker<T> createMockSingerWorker(Supplier<Process> runFn, Supplier<T> getOutputFn) {
    return new BaseSingerWorker(
        UUID.randomUUID().toString(),
        getWorkspacePath().toAbsolutePath().toString(),
        "/fake/singer/root") {
      @Override
      protected Process runInternal() {
        return runFn.get();
      }

      @Override
      protected Object getOutputInternal() {
        return getOutputFn.get();
      }
    };
  }
}

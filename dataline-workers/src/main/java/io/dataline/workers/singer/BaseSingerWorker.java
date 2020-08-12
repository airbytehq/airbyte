package io.dataline.workers.singer;

import io.dataline.workers.Worker;
import io.dataline.workers.WorkerOutputAndStatus;
import io.dataline.workers.WorkerStatus;
import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseSingerWorker<OutputType> implements Worker<OutputType> {
  private static Logger LOGGER = LoggerFactory.getLogger(BaseSingerWorker.class);

  protected String workerId;
  protected Process workerProcess;

  private final String workspaceRoot;
  private final String singerRoot;
  private WorkerStatus workerStatus;

  protected BaseSingerWorker(String workerId, String workspaceRoot, String singerRoot) {
    this.workerId = workerId;
    this.workspaceRoot = workspaceRoot;
    this.singerRoot = singerRoot;

    this.workerStatus = WorkerStatus.NOT_STARTED;
  }

  @Override
  public WorkerStatus getStatus() {
    return workerStatus;
  }

  @Override
  public WorkerOutputAndStatus run() {
    if (!getStatus().equals(WorkerStatus.NOT_STARTED)) {
      LOGGER.debug(
          "Attempted to run worker {} which has already started and has status {}",
          workerId,
          getStatus());

      return;
    }
    try {
      transitionStatusIfValid(WorkerStatus.IN_PROGRESS);
      workerProcess = runInternal();
      workerProcess.wait();
      transitionStatusIfValid(WorkerStatus.COMPLETED);
      return getOutputInternal();
    } catch (Exception e) {
      // In the case that the worker itself fails, not its underlying process (e.g: connection test
      // fails), we count this as a failed worker and re-throw. The process monitoring this worker
      // is responsible for reporting this error correctly.
      transitionStatusIfValid(WorkerStatus.FAILED);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void cancel() {
    try {
      if (!getStatus().equals(WorkerStatus.IN_PROGRESS)
          && !getStatus().equals(WorkerStatus.NOT_STARTED)) {
        LOGGER.debug("Tried to cancel Worker {} in terminal status {}.", workerId, getStatus());
        return;
      }

      workerProcess.destroy();
      workerProcess.wait(TimeUnit.SECONDS.toMillis(10));
      if (workerProcess.isAlive()) {
        workerProcess.destroyForcibly();
      }

      transitionStatusIfValid(WorkerStatus.CANCELLED);
    } catch (InterruptedException e) {
      transitionStatusIfValid(WorkerStatus.FAILED);
      throw new RuntimeException(e);
    }
  }

  @Override
  public OutputType getOutput() {
    if (!inTerminalStatus()) {
      throw new IllegalStateException(
          "Can only get output when worker is in a terminal status. Worker status: " + getStatus());
    }

    return getOutputInternal();
  }

  // TODO add getError and have base worker redirect standard

  protected Path getWorkspacePath() {
    return Paths.get(workspaceRoot, workerId);
  }

  protected String readFileFromWorkspace(String fileName) {
    try (FileReader fileReader = new FileReader(getWorkspaceFilePath(fileName));
        BufferedReader br = new BufferedReader(fileReader)) {
      return br.lines().collect(Collectors.joining("\n"));
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String writeFileToWorkspace(String fileName, String contents) {
    String filePath = getWorkspaceFilePath(fileName);
    try (FileWriter fileWriter = new FileWriter(filePath)) {
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String getExecutableAbsolutePath(SingerConnector tapOrTarget) {
    return Paths.get(
            singerRoot,
            tapOrTarget.getPythonVirtualEnvName(),
            "bin",
            tapOrTarget.getExecutableName())
        .toAbsolutePath()
        .toString();
  }

  private String getWorkspaceFilePath(String fileName) {
    return getWorkspacePath().resolve(fileName).toAbsolutePath().toString();
  }

  private boolean inTerminalStatus() {
    return WorkerStatus.TERMINAL_STATUSES.contains(getStatus());
  }

  // returns true if the state transition was valid and completed
  private boolean transitionStatusIfValid(WorkerStatus to) {
    boolean validTransition;
    WorkerStatus from = workerStatus;
    switch (from) {
      case NOT_STARTED:
        validTransition = true;
        break;
      case IN_PROGRESS:
        validTransition = !to.equals(WorkerStatus.NOT_STARTED);
        break;
      case CANCELLED:
      case FAILED:
      case COMPLETED:
        validTransition = false;
        break;
      default:
        throw new RuntimeException("Unknown initial state: " + from);
    }
    if (validTransition) {
      workerStatus = to;
    } else {
      LOGGER.debug("Invalid state transition for worker {} from {} to {} ", workerId, from, to);
    }

    return validTransition;
  }

  /** Starts the necessary Singer CLI process and returns a handle to its {@link Process} */
  protected abstract Process runInternal();

  /** Run when the consumer asks for the output AND the worker has successfully COMPLETED */
  protected abstract OutputType getOutputInternal();
}

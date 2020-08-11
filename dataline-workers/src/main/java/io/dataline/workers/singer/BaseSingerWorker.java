package io.dataline.workers.singer;

import io.dataline.workers.Worker;
import io.dataline.workers.WorkerStatus;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public abstract class BaseSingerWorker<OutputType> implements Worker<OutputType> {
  private static String WORKSPACES_ROOT = "workspace/worker/";
  private static String SINGER_LIBS_ROOT = "lib/singer";

  protected String workerId;
  protected Process workerProcess;

  private WorkerStatus workerStatus;
  private Thread statusMonitor;

  protected BaseSingerWorker(String workerId) {
    this.workerId = workerId;
    this.workerStatus = WorkerStatus.NOT_STARTED;
  }

  @Override
  public WorkerStatus getStatus() {
    return workerStatus;
  }

  @Override
  public void run() {
    if (!getStatus().equals(WorkerStatus.NOT_STARTED)) {
      // TODO debug log
      return;
    }

    try {
      workerProcess = runInternal();
      workerStatus = WorkerStatus.IN_PROGRESS;
      monitorProcessStatus(workerProcess);
    } catch (Exception e) {
      workerStatus = WorkerStatus.FAILED;
    }
  }

  @Override
  public void cancel() {
    if (!getStatus().equals(WorkerStatus.IN_PROGRESS)
        && !getStatus().equals(WorkerStatus.NOT_STARTED)) {
      // TODO debug log
      return;
    }

    statusMonitor.interrupt();
    workerProcess.destroy();
    try {
      Thread.sleep(TimeUnit.SECONDS.toMillis(2));
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
    if (workerProcess.isAlive()) {
      workerProcess.destroyForcibly();
    }

    workerStatus = WorkerStatus.CANCELLED;
  }

  @Override
  public OutputType getOutput() {
    if (!getStatus().equals(WorkerStatus.COMPLETED)) {
      throw new IllegalStateException(
          "Can only get output when worker is COMPLETED. Worker status: " + getStatus());
    }

    return getOutputInternal();
  }

  // TODO add getError and have base worker redirect standard

  protected Path getWorkspacePath() {
    return Paths.get(WORKSPACES_ROOT, workerId);
  }

  protected String readFileFromWorkspace(String fileName) {
    try {
      FileReader fileReader = new FileReader(getWorkspaceFilePath(fileName));
      BufferedReader br = new BufferedReader(fileReader);
      return br.lines().collect(Collectors.joining("\n"));
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    }
  };

  protected String writeFileToWorkspace(String fileName, String contents) {
    try {
      String filePath = getWorkspaceFilePath(fileName);
      FileWriter fileWriter = new FileWriter(filePath);
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String getExecutableAbsolutePath(ISingerTapOrTarget tapOrTarget) {
    return Paths.get(
            SINGER_LIBS_ROOT,
            tapOrTarget.getPythonVirtualEnvName(),
            "bin",
            tapOrTarget.getExecutableName())
        .toAbsolutePath()
        .toString();
  }

  private void monitorProcessStatus(final Process p) {
    statusMonitor =
        new Thread(
            () -> {
              waitUntilProcessExits(p);
              workerStatus = WorkerStatus.COMPLETED;
            });
    statusMonitor.start();
  }

  private String getWorkspaceFilePath(String fileName) {
    return getWorkspacePath().resolve(fileName).toAbsolutePath().toString();
  }

  private void waitUntilProcessExits(Process p) {
    try {
      while (!p.waitFor(0, TimeUnit.MILLISECONDS)) {
        Thread.sleep(TimeUnit.SECONDS.toMillis(2));
      }
    } catch (InterruptedException e) {

    }
  }

  /** Runs the necessary Singer CLI process and returns a handle to its {@link Process} */
  protected abstract Process runInternal();

  /** Run when the consumer asks for the output AND the worker has successfully COMPLETED * */
  protected abstract OutputType getOutputInternal();
}

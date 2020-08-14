package io.dataline.workers.singer;

import static io.dataline.workers.JobStatus.*;

import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseSingerWorker<OutputType> implements Worker<OutputType> {
  private static Logger LOGGER = LoggerFactory.getLogger(BaseSingerWorker.class);

  protected JobStatus jobStatus;
  protected String workerId;
  protected Process workerProcess;
  protected final Path workspacePath;

  private final String singerRoot;

  protected BaseSingerWorker(String workerId, String workspaceRoot, String singerRoot) {
    this.workerId = workerId;
    this.workspacePath = Path.of(workspaceRoot, workerId);
    this.singerRoot = singerRoot;
  }

  @Override
  public OutputAndStatus<OutputType> run() {
    createWorkspace();
    try {
      return runInternal();
    } finally {
    }
  }

  public abstract OutputAndStatus<OutputType> runInternal();

  private void createWorkspace() {
    try {
      FileUtils.forceMkdir(workspacePath.toFile());
    } catch (IOException e) {
      LOGGER.error("Unable to create workspace for worker {} due to exception {} ", workerId, e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void cancel() {
    try {
      jobStatus = FAILED;
      workerProcess.destroy();
      workerProcess.wait(TimeUnit.SECONDS.toMillis(10));
      if (workerProcess.isAlive()) {
        workerProcess.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when cancelling worker " + workerId, e);
    }
  }

  protected Path getWorkspacePath() {
    return workspacePath;
  }

  protected String readFileFromWorkspace(String fileName) {
    try (FileReader fileReader = new FileReader(getWorkspaceFilePath(fileName));
        BufferedReader br = new BufferedReader(fileReader)) {
      return br.lines().collect(Collectors.joining("\n"));
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
}

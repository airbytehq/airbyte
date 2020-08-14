package io.dataline.workers.singer;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;

import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.OutputAndStatus;
import java.io.File;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDiscoveryWorker extends BaseSingerWorker<DiscoveryOutput> {
  // TODO log errors to specified file locations
  private static Logger LOGGER = LoggerFactory.getLogger(SingerDiscoveryWorker.class);
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private final String configDotJson;
  private final SingerTap tap;

  public SingerDiscoveryWorker(
      String workerId,
      String configDotJson,
      SingerTap tap,
      String workspaceRoot,
      String singerLibsRoot) {
    super(workerId, workspaceRoot, singerLibsRoot);
    this.configDotJson = configDotJson;
    this.tap = tap;
  }

  @Override
  public OutputAndStatus<DiscoveryOutput> runInternal() {
    // TODO use format converter here
    // write config.json to disk
    String configPath = writeFileToWorkspace(CONFIG_JSON_FILENAME, configDotJson);

    String tapPath = getExecutableAbsolutePath(tap);

    String catalogDotJsonPath =
        getWorkspacePath().resolve(CATALOG_JSON_FILENAME).toAbsolutePath().toString();
    String errorLogPath =
        getWorkspacePath().resolve(ERROR_LOG_FILENAME).toAbsolutePath().toString();
    // exec
    try {

      String[] cmd = {tapPath, "--config", configPath, "--discover"};

      Process workerProcess =
          new ProcessBuilder(cmd)
              .redirectError(new File(errorLogPath))
              .redirectOutput(new File(catalogDotJsonPath))
              .start();

      // TODO will need to wrap this synchronize in a while loop and timeout to prevent contention
      // coming from
      //  cancellations
      synchronized (workerProcess) {
        workerProcess.wait();
      }
      int exitCode = workerProcess.exitValue();
      if (exitCode == 0) {
        String catalog = readFileFromWorkspace(CATALOG_JSON_FILENAME);
        return new OutputAndStatus<>(SUCCESSFUL, new DiscoveryOutput(catalog));
      } else {
        LOGGER.debug(
            "Discovery worker {} subprocess finished with exit code {}", workerId, exitCode);
        return new OutputAndStatus<>(FAILED);
      }
    } catch (IOException | InterruptedException e) {
      LOGGER.error("Exception running discovery: ", e);
      throw new RuntimeException(e);
    }
  }
}

package io.airbyte.workers.process;

import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(SingerIntegrationLauncher.class);

  private String imageName;
  private ProcessBuilderFactory pbf;

  public SingerIntegrationLauncher(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public ProcessBuilder spec(Path jobRoot) throws WorkerException {

    throw new NotImplementedException("getSpec doesn't exist for singer images");
  }

  @Override
  public ProcessBuilder check(final Path jobRoot, final String configFilename) throws WorkerException {
    return discover(jobRoot, configFilename);
  }

  @Override
  public ProcessBuilder discover(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(jobRoot, imageName,
        "--config", configFilename,
        "--discover");
  }

  @Override
  public ProcessBuilder read(final Path jobRoot, final String configFilename, final String catalogFilename, final String stateFilename)
      throws WorkerException {
    String[] cmd = {
        "--config",
        configFilename,
        "--properties",
        catalogFilename
    };

    if (stateFilename != null) {
      cmd = ArrayUtils.addAll(cmd, "--state", stateFilename);
    }

    return pbf.create(jobRoot, imageName, cmd);
  }

  @Override
  public ProcessBuilder write(Path jobRoot, String configFilename, String catalogFilename) throws WorkerException {
    return pbf.create(jobRoot, imageName, "--config", WorkerConstants.TARGET_CONFIG_JSON_FILENAME);
  }
}

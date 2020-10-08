package io.airbyte.workers.process;

import com.google.common.collect.Lists;
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(AirbyteIntegrationLauncher.class);

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  public AirbyteIntegrationLauncher(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public ProcessBuilder spec(final Path jobRoot) throws WorkerException {
    return pbf.create(
        jobRoot,
        imageName,
        "spec"
    );
  }

  @Override
  public ProcessBuilder check(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(
        jobRoot,
        imageName,
        "check",
        "--config", configFilename
    );
  }

  @Override
  public ProcessBuilder discover(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(
        jobRoot,
        imageName,
        "discover",
        "--config", configFilename
    );
  }

  @Override
  public ProcessBuilder read(final Path jobRoot,
                             final String configFilename,
                             final String catalogFilename,
                             final String stateFilename) throws WorkerException {
    final List<String> arguments = Lists.newArrayList(
        "read",
        "--config", configFilename,
        "--catalog", catalogFilename);

    if (stateFilename != null) {
      arguments.add("--state");
      arguments.add(stateFilename);
    }

    return pbf.create(jobRoot, imageName, arguments);
  }

  @Override public ProcessBuilder write(Path jobRoot, String configFilename, String catalogFilename) throws WorkerException {
    return pbf.create(jobRoot, imageName,
        "write",
        "--config", configFilename,
        "--catalog", catalogFilename
    );
  }
}

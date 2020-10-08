package io.airbyte.workers;

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.workers.process.ProcessBuilderFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;

public class DefaultGetSpecWorker implements GetSpecWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecWorker.class);

  private final ProcessBuilderFactory processBuilderFactory;

  private Process process;

  public DefaultGetSpecWorker(ProcessBuilderFactory processBuilderFactory) {
    this.processBuilderFactory = processBuilderFactory;
  }

  @Override
  public OutputAndStatus<StandardGetSpecOutput> run(JobGetSpecConfig config, Path jobRoot) {
    String imageName = config.getDockerImage();
    try {
      process = processBuilderFactory.create(jobRoot, imageName, "--spec").start();
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      try (InputStream stdout = process.getInputStream()) {
        // retrieving spec should generally be instantaneous
        WorkerUtils.gentleClose(process, 10, TimeUnit.SECONDS);

        if (process.exitValue() == 0) {
          String specString = new String(stdout.readAllBytes());
          ConnectorSpecification spec = Jsons.deserialize(specString, ConnectorSpecification.class);
          return new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardGetSpecOutput().withSpecification(spec));
        } else {
          return new OutputAndStatus<>(JobStatus.FAILED);
        }
      }

    } catch (Exception e) {
      LOGGER.error("Error while getting spec from image {}: {}", imageName, e);
      return new OutputAndStatus<>(JobStatus.FAILED);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }
}

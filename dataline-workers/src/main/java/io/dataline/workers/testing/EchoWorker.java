package io.dataline.workers.testing;

import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EchoWorker implements Worker<String> {
  private static final Logger LOGGER = LoggerFactory.getLogger(EchoWorker.class);

  public EchoWorker() {}

  @Override
  public OutputAndStatus<String> run() {
    LOGGER.info("Hello World");
    return new OutputAndStatus<>(JobStatus.SUCCESSFUL, "echoed");
  }

  @Override
  public void cancel() {
    // no-op
  }
}

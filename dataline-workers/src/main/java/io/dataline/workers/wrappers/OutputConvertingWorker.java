package io.dataline.workers.wrappers;

import io.dataline.config.JobOutput;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.nio.file.Path;

abstract class OutputConvertingWorker<InputType, OriginalOutputType, FinalOutputType> implements Worker<InputType, FinalOutputType> {

  private final Worker<InputType, OriginalOutputType> innerWorker;

  public OutputConvertingWorker(Worker<InputType, OriginalOutputType> innerWorker) {
    this.innerWorker = innerWorker;
  }

  @Override
  public OutputAndStatus<FinalOutputType> run(InputType config, Path jobRoot) throws InvalidCredentialsException, InvalidCatalogException {
    OutputAndStatus<OriginalOutputType> run = innerWorker.run(config, jobRoot);
    if (run.getOutput().isPresent()) {
      return new OutputAndStatus<FinalOutputType>(run.getStatus(), convert(run.getOutput().get()));
    } else {
      return new OutputAndStatus<>(run.getStatus());
    }
  }

  @Override
  public void cancel() {
    innerWorker.cancel();
  }

  protected abstract FinalOutputType convert(OriginalOutputType output);
}

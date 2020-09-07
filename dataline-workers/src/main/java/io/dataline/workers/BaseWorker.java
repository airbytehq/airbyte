package io.dataline.workers;

import com.google.common.annotations.VisibleForTesting;
import io.dataline.config.JobOutput;
import java.nio.file.Path;

abstract class BaseWorker<InputType, OutputType> implements Worker<InputType> {
  @VisibleForTesting
  protected abstract OutputAndStatus<OutputType> runInternal(InputType inputType, Path jobRoot)
      throws InvalidCredentialsException, InvalidCatalogException;

  protected abstract JobOutput toJobOutput(OutputType output);

  @Override
  public OutputAndStatus<JobOutput> run(InputType input, Path jobRoot) throws InvalidCredentialsException, InvalidCatalogException {
    OutputAndStatus<OutputType> outputAndStatus = runInternal(input, jobRoot);
    if (outputAndStatus.getOutput().isPresent()) {
      return new OutputAndStatus<>(outputAndStatus.getStatus(), toJobOutput(outputAndStatus.getOutput().get()));
    } else {
      return new OutputAndStatus<>(outputAndStatus.getStatus());
    }
  }
}

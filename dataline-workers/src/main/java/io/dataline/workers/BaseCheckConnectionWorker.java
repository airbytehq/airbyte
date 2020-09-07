package io.dataline.workers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;

public abstract class BaseCheckConnectionWorker extends BaseWorker<StandardCheckConnectionInput, StandardCheckConnectionOutput>
    implements CheckConnectionWorker {

  @Override
  protected JobOutput toJobOutput(StandardCheckConnectionOutput output) {
    return new JobOutput()
        .withOutputType(JobOutput.OutputType.CHECK_CONNECTION)
        .withCheckConnection(output);
  }
}

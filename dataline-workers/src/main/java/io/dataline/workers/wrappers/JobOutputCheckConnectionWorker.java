package io.dataline.workers.wrappers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.Worker;

public class JobOutputCheckConnectionWorker extends OutputConvertingWorker<StandardCheckConnectionInput, StandardCheckConnectionOutput, JobOutput> {

  public JobOutputCheckConnectionWorker(CheckConnectionWorker innerWorker) {
    super(innerWorker);
  }

  @Override
  protected JobOutput convert(StandardCheckConnectionOutput output) {
    return new JobOutput().withOutputType(JobOutput.OutputType.CHECK_CONNECTION).withCheckConnection(output);
  }
}

package io.dataline.workers.wrappers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.DiscoverSchemaWorker;

public class JobOutputDiscoverSchemaWorker extends OutputConvertingWorker<StandardDiscoverSchemaInput, StandardDiscoverSchemaOutput, JobOutput> {

  public JobOutputDiscoverSchemaWorker(DiscoverSchemaWorker innerWorker) {
    super(innerWorker);
  }

  @Override
  protected JobOutput convert(StandardDiscoverSchemaOutput output) {
    return new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_SCHEMA).withDiscoverSchema(output);
  }
}

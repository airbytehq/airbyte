package io.dataline.workers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;

public abstract class BaseDiscoverSchemaWorker extends BaseWorker<StandardDiscoverSchemaInput, StandardDiscoverSchemaOutput>
    implements DiscoverSchemaWorker {

  @Override
  protected JobOutput toJobOutput(StandardDiscoverSchemaOutput output) {
    return new JobOutput()
        .withOutputType(JobOutput.OutputType.DISCOVER_SCHEMA)
        .withDiscoverSchema(output);
  }
}

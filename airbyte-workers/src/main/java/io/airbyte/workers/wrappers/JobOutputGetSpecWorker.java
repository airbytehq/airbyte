package io.airbyte.workers.wrappers;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.workers.GetSpecWorker;

public class JobOutputGetSpecWorker extends OutputConvertingWorker<JobGetSpecConfig, StandardGetSpecOutput, JobOutput> {

  public JobOutputGetSpecWorker(GetSpecWorker innerWorker) {
    super(
        innerWorker,
        standardGetSpecOutput -> new JobOutput().withOutputType(JobOutput.OutputType.GET_SPEC).withGetSpec(standardGetSpecOutput)
    );
  }
}

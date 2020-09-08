package io.dataline.workers.wrappers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.workers.SyncWorker;

public class JobOutputSyncWorker extends OutputConvertingWorker<StandardSyncInput, StandardSyncOutput, JobOutput> {

  public JobOutputSyncWorker(SyncWorker innerWorker) {
    super(innerWorker);
  }

  @Override protected JobOutput convert(StandardSyncOutput output) {
    return new JobOutput().withOutputType(JobOutput.OutputType.SYNC).withSync(output);
  }
}

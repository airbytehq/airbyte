package io.dataline.workers;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;

abstract class BaseSyncWorker extends BaseWorker<StandardSyncInput, StandardSyncOutput> implements SyncWorker {
  @Override protected JobOutput toJobOutput(StandardSyncOutput output) {
    return new JobOutput()
        .withOutputType(JobOutput.OutputType.SYNC)
        .withSync(output);
  }
}

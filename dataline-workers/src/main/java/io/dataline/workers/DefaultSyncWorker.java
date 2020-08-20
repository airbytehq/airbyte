package io.dataline.workers;

import io.dataline.config.JobSyncConfig;
import io.dataline.config.JobSyncOutput;
import io.dataline.config.JobSyncTapConfig;
import io.dataline.config.JobSyncTargetConfig;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.stream.Stream;

public class DefaultSyncWorker<T> implements SyncWorker {
  private final SyncTap<T> tap;
  private final SyncTarget<T> target;

  // todo (cgardens) - each worker probably doesn't need the whole job config.
  public DefaultSyncWorker(SyncTap<T> tap, SyncTarget<T> target) {
    this.tap = tap;
    this.target = target;
  }

  @Override
  public OutputAndStatus<JobSyncOutput> run(JobSyncConfig syncConfig, String workspacePath)
      throws InvalidCredentialsException, InvalidCatalogException {

    final JobSyncTapConfig tapConfig = new JobSyncTapConfig();
    tapConfig.setSourceConnectionImplementation(syncConfig.getSourceConnectionImplementation());
    tapConfig.setStandardSync(syncConfig.getStandardSync());

    final JobSyncTargetConfig targetConfig = new JobSyncTargetConfig();
    targetConfig.setDestinationConnectionImplementation(
        syncConfig.getDestinationConnectionImplementation());
    targetConfig.setStandardSync(syncConfig.getStandardSync());

    final JobSyncOutput output =
        target.run(tap.run(tapConfig, workspacePath), targetConfig, workspacePath);

    // todo (cgardens) - OutputAndStatus doesn't really work here. it's like both tap and target
    //   need to return a promise for OutputAndStatus creation. But then that's kinda confusing too.
    return new OutputAndStatus<>(JobStatus.SUCCESSFUL, output);
  }

  @Override
  public void cancel() {}

  public interface SyncTap<T> {
    Stream<T> run(JobSyncTapConfig jobSyncTapConfig, String workspacePath);
  }

  public interface SyncTarget<T> {
    JobSyncOutput run(
        Stream<T> data, JobSyncTargetConfig jobSyncTargetConfig, String workspacePath);
  }
}

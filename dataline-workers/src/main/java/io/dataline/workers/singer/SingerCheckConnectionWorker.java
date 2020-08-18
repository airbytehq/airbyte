package io.dataline.workers.singer;

import io.dataline.workers.CheckConnectionOutput;
import io.dataline.workers.OutputAndStatus;

public class SingerCheckConnectionWorker extends BaseSingerWorker<CheckConnectionOutput> {
  private SingerDiscoveryWorker singerDiscoveryWorker;

  public SingerCheckConnectionWorker(
      String workerId,
      SingerConnector tapOrTarget,
      String configDotJson,
      String workspaceRoot,
      String singerLibsRoot) {
    super(workerId, workspaceRoot, singerLibsRoot);
    this.singerDiscoveryWorker =
        new SingerDiscoveryWorker(
            workerId, configDotJson, tapOrTarget, workspaceRoot, singerLibsRoot);
  }

  @Override
  OutputAndStatus<CheckConnectionOutput> runInternal() {
    singerDiscoveryWorker.runInternal();
  }
}

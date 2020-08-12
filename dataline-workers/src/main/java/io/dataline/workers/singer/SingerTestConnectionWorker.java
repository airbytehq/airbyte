package io.dataline.workers.singer;

public class SingerTestConnectionWorker {
  private final SingerConnector tapOrTarget;
  private final String configDotJson;

  public SingerTestConnectionWorker(SingerConnector tapOrTarget, String configDotJson) {

    this.tapOrTarget = tapOrTarget;
    this.configDotJson = configDotJson;
  }
}

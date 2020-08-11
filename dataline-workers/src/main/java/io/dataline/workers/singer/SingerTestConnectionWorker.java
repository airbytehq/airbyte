package io.dataline.workers.singer;

public class SingerTestConnectionWorker {
  private final ISingerTapOrTarget tapOrTarget;
  private final String configDotJson;

  // TODO
  public SingerTestConnectionWorker(ISingerTapOrTarget tapOrTarget, String configDotJson) {

    this.tapOrTarget = tapOrTarget;
    this.configDotJson = configDotJson;
  }
}

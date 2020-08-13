package io.dataline.workers.singer;

public class SingerSyncWorker {
  private final SingerTap tap;
  private final String tapConfiguration;
  private final String tapCatalog;
  private final String state;
  private final SingerTarget target;
  private final String targetConfig;

  // TODO
  public SingerSyncWorker(
      SingerTap tap,
      String tapConfiguration,
      String tapCatalog,
      String state,
      SingerTarget target,
      String targetConfig) {

    this.tap = tap;
    this.tapConfiguration = tapConfiguration;
    this.tapCatalog = tapCatalog;
    this.state = state;
    this.target = target;
    this.targetConfig = targetConfig;
  }
}

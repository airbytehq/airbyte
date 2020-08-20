package io.dataline.workers.singer.postgres_tap;

import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoveryWorker;

import static io.dataline.workers.singer.postgres_tap.PostgresSingerTapConstants.POSTGRES_SINGER_TAP;


public class SingerPostgresTapDiscoverWorker extends SingerDiscoveryWorker {
  public SingerPostgresTapDiscoverWorker() {
    super(POSTGRES_SINGER_TAP);
  }
}

package io.dataline.workers.singer.postgres_tap;

import io.dataline.workers.singer.SingerCheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoveryWorker;

import static io.dataline.workers.singer.postgres_tap.PostgresSingerTapConstants.POSTGRES_SINGER_TAP;

public class SingerPostgresTapCheckConnectionWorker extends SingerCheckConnectionWorker {
  public SingerPostgresTapCheckConnectionWorker() {
    super(POSTGRES_SINGER_TAP);
  }
}

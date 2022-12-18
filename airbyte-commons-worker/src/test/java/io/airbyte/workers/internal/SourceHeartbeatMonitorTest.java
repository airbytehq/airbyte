/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SourceHeartbeatMonitorTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceHeartbeatMonitorTest.class);

  @Test
  void test() {
    // final HeartbeatMonitor heartbeatMonitor = mock(HeartbeatMonitor.class);
    // doReturn(false).when(heartbeatMonitor).isBeating();
    //
    // try(final SourceHeartbeatMonitor srcHeartbeatMonitor = new
    // SourceHeartbeatMonitor(heartbeatMonitor, 10, TimeUnit.MILLISECONDS)) {
    // while(true) {
    // LOGGER.info("infinite loop");
    // try {
    // sleep(100);
    // } catch (final InterruptedException e) {
    // LOGGER.info("interrupted.");
    // }
    // }
    // } catch (final Exception e) {
    // LOGGER.info("exception from autocloseable.");
    // }
  }

}

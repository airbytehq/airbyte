/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class KubeProcessFactoryTest {

  @Test
  void getPodNameNormal() {
    var name = KubeProcessFactory.createPodName("airbyte/tester:1", "1", 10);
    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("tester-worker-1-10-", withoutRandSuffix);
  }

  @Test
  void getPodNameTruncated() {
    var name = KubeProcessFactory.createPodName("airbyte/very-very-very-long-name-longer-than-63-chars:2", "1", 10);
    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("very-very-very-long-name-longer-than-63-chars-worker-1-10-", withoutRandSuffix);
  }

  @Test
  void testHandlingDashAsFirstCharacter() {
    var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    var name = KubeProcessFactory.createPodName("airbyte/source-google-adwordsv2:latest", uuid, 10);

    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("adwordsv2-worker-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

  @Test
  void testOnlyDashes() {
    var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    var name = KubeProcessFactory.createPodName("--------", uuid, 10);

    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("worker-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

  @Test
  void testOnlyNumeric() {
    var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    var name = KubeProcessFactory.createPodName("0000000000", uuid, 10);

    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("worker-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

}

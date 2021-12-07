/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class KubeProcessFactoryTest {

  @Test
  void getPodNameNormal() {
    final var name = KubeProcessFactory.createPodName("airbyte/tester:1", "1", 10);
    final var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("tester-sync-1-10-", withoutRandSuffix);
  }

  @Test
  void getPodNameTruncated() {
    final var name = KubeProcessFactory.createPodName("airbyte/very-very-very-long-name-longer-than-63-chars:2", "1", 10);
    final var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("very-very-very-long-name-longer-than-63-chars-sync-1-10-", withoutRandSuffix);
  }

  @Test
  void testHandlingDashAsFirstCharacter() {
    final var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    final var name = KubeProcessFactory.createPodName("airbyte/source-google-adwordsv2:latest", uuid, 10);

    final var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("le-adwordsv2-sync-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

  @Test
  void testOnlyDashes() {
    final var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    final var name = KubeProcessFactory.createPodName("--------", uuid, 10);

    final var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("sync-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

  @Test
  void testOnlyNumeric() {
    final var uuid = "7339ba3b-cb53-4210-9591-c70d4a372330";
    final var name = KubeProcessFactory.createPodName("0000000000", uuid, 10);

    System.out.println(name);
    final var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("sync-7339ba3b-cb53-4210-9591-c70d4a372330-10-", withoutRandSuffix);
  }

}

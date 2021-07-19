package io.airbyte.workers.process;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class KubeProcessFactoryTest {

  @Test
  void getPodNameNormal() {
    var name = KubeProcessFactory.getPodName("airbyte/tester", "1", 10);
    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("tester-worker-1-10-", withoutRandSuffix);
  }

  @Test
  void getPodNameTruncated() {
    var name = KubeProcessFactory.getPodName("airbyte/very-very-very-long-name-longer-than-63-chars", "1", 10);
    var withoutRandSuffix = name.substring(0, name.length() - 5);
    Assertions.assertEquals("very-very-very-long-name-longer-than-63-chars-worker-1-10-", withoutRandSuffix);
  }

}

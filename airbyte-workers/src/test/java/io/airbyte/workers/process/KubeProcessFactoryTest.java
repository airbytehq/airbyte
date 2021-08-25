/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

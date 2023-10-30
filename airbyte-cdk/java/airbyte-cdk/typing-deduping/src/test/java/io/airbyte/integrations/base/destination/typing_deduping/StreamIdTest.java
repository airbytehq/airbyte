/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class StreamIdTest {

  /**
   * Both these streams naively want the same raw table name ("aaa_abab_bbb_abab_ccc"). Verify that
   * they don't actually use the same raw table.
   */
  @Test
  public void rawNameCollision() {
    String stream1 = StreamId.concatenateRawTableName("aaa_abab_bbb", "ccc");
    String stream2 = StreamId.concatenateRawTableName("aaa", "bbb_abab_ccc");

    assertAll(
        () -> assertEquals("aaa_abab_bbb_raw__stream_ccc", stream1),
        () -> assertEquals("aaa_raw__stream_bbb_abab_ccc", stream2));
  }

  @Test
  public void noUnderscores() {
    String stream = StreamId.concatenateRawTableName("a", "b");

    assertEquals("a_raw__stream_b", stream);
  }

}

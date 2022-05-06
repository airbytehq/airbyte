/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.config.FailureReason;
import io.airbyte.config.Metadata;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

public class FailureHelperTest {

  private static final FailureReason TRACE_FAILURE_REASON = new FailureReason()
      .withInternalMessage("internal message")
      .withStacktrace("stack trace")
      .withTimestamp(Long.valueOf(1111112))
      .withMetadata(new Metadata()
          .withAdditionalProperty("jobId", 12345)
          .withAdditionalProperty("attempt", 1)
          .withAdditionalProperty("from_trace_message", true));

  private static final FailureReason EXCEPTION_FAILURE_REASON = new FailureReason()
      .withInternalMessage("internal message")
      .withStacktrace("stack trace")
      .withTimestamp(Long.valueOf(1111111))
      .withMetadata(new Metadata()
          .withAdditionalProperty("jobId", 12345)
          .withAdditionalProperty("attempt", 1));

  @Test
  public void testOrderedFailures() throws Exception {
    final List<FailureReason> failureReasonList = FailureHelper.orderedFailures(Set.of(TRACE_FAILURE_REASON, EXCEPTION_FAILURE_REASON));
    assertEquals(failureReasonList.get(0), TRACE_FAILURE_REASON);
  }

}

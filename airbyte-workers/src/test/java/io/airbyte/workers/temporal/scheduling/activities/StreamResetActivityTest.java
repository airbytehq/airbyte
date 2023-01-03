/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivity.DeleteStreamResetRecordsForJobInput;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class StreamResetActivityTest {

  @Mock
  private StreamResetRecordsHelper streamResetRecordsHelper;
  @InjectMocks
  private StreamResetActivityImpl streamResetActivity;

  @Test
  void testDeleteStreamResetRecordsForJob() {
    final DeleteStreamResetRecordsForJobInput input = new DeleteStreamResetRecordsForJobInput(UUID.randomUUID(), Long.valueOf("123"));
    streamResetActivity.deleteStreamResetRecordsForJob(input);
    verify(streamResetRecordsHelper).deleteStreamResetRecordsForJob(eq(input.getJobId()), eq(input.getConnectionId()));
  }

}

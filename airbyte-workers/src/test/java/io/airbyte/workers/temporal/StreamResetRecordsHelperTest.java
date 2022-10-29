/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * Test suite for the {@link StreamResetRecordsHelper} class.
 */
@ExtendWith(MockitoExtension.class)
class StreamResetRecordsHelperTest {

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final Long JOB_ID = Long.valueOf("123");

  @Mock
  private JobPersistence jobPersistence;
  @Mock
  private StreamResetPersistence streamResetPersistence;
  @InjectMocks
  private StreamResetRecordsHelper streamResetRecordsHelper;

  @Test
  void testDeleteStreamResetRecordsForJob() throws IOException {
    final Job jobMock = mock(Job.class, RETURNS_DEEP_STUBS);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(jobMock);

    when(jobMock.getConfig().getConfigType()).thenReturn(ConfigType.RESET_CONNECTION);
    final List<StreamDescriptor> streamsToDelete = List.of(new StreamDescriptor().withName("streamname").withNamespace("namespace"));
    when(jobMock.getConfig().getResetConnection().getResetSourceConfiguration().getStreamsToReset()).thenReturn(streamsToDelete);
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(JOB_ID, CONNECTION_ID);
    Mockito.verify(streamResetPersistence).deleteStreamResets(CONNECTION_ID, streamsToDelete);
  }

  @Test
  void testIncorrectConfigType() throws IOException {
    final Job jobMock = mock(Job.class, RETURNS_DEEP_STUBS);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(jobMock);

    when(jobMock.getConfig().getConfigType()).thenReturn(ConfigType.SYNC);
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(JOB_ID, CONNECTION_ID);
    Mockito.verify(streamResetPersistence, never()).deleteStreamResets(Mockito.any(UUID.class), Mockito.anyList());
  }

  @Test
  void testNoJobId() throws IOException {
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(null, CONNECTION_ID);
    Mockito.verify(jobPersistence, never()).getJob(Mockito.anyLong());
    Mockito.verify(streamResetPersistence, never()).deleteStreamResets(Mockito.any(UUID.class), Mockito.anyList());
  }

}

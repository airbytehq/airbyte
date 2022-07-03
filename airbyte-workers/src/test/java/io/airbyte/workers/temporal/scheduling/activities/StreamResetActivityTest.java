/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivity.DeleteStreamResetRecordsForJobInput;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class StreamResetActivityTest {

  @Mock
  private StreamResetPersistence streamResetPersistence;
  @Mock
  private JobPersistence jobPersistence;
  @InjectMocks
  private StreamResetActivityImpl streamResetActivity;
  private final DeleteStreamResetRecordsForJobInput input = new DeleteStreamResetRecordsForJobInput(UUID.randomUUID(), Long.valueOf("123"));
  private final DeleteStreamResetRecordsForJobInput noJobIdInput = new DeleteStreamResetRecordsForJobInput(UUID.randomUUID(), null);

  @Test
  public void testDeleteStreamResetRecordsForJob() throws IOException {
    final Job jobMock = mock(Job.class, RETURNS_DEEP_STUBS);
    when(jobPersistence.getJob(input.getJobId())).thenReturn(jobMock);

    when(jobMock.getConfig().getConfigType()).thenReturn(ConfigType.RESET_CONNECTION);
    final List<StreamDescriptor> streamsToDelete = List.of(new StreamDescriptor().withName("streamname").withNamespace("namespace"));
    when(jobMock.getConfig().getResetConnection().getResetSourceConfiguration().getStreamsToReset()).thenReturn(streamsToDelete);
    streamResetActivity.deleteStreamResetRecordsForJob(input);
    Mockito.verify(streamResetPersistence).deleteStreamResets(input.getConnectionId(), streamsToDelete);
  }

  @Test
  public void testIncorrectConfigType() throws IOException {
    final Job jobMock = mock(Job.class, RETURNS_DEEP_STUBS);
    when(jobPersistence.getJob(input.getJobId())).thenReturn(jobMock);

    when(jobMock.getConfig().getConfigType()).thenReturn(ConfigType.SYNC);
    streamResetActivity.deleteStreamResetRecordsForJob(input);
    Mockito.verify(streamResetPersistence, never()).deleteStreamResets(Mockito.any(UUID.class), Mockito.anyList());
  }

  @Test
  public void testNoJobId() throws IOException {
    streamResetActivity.deleteStreamResetRecordsForJob(noJobIdInput);
    Mockito.verify(jobPersistence, never()).getJob(Mockito.anyLong());
    Mockito.verify(streamResetPersistence, never()).deleteStreamResets(Mockito.any(UUID.class), Mockito.anyList());
  }

}

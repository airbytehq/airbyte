/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.temporal.scheduling.TaskQueueMapper;
import io.airbyte.config.Geography;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * Test suite for the {@link RouterService} class.
 */
@ExtendWith(MockitoExtension.class)
class RouterServiceTest {

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String US_TASK_QUEUE = "US_TASK_QUEUE";
  private static final String EU_TASK_QUEUE = "EU_TASK_QUEUE";

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private TaskQueueMapper mTaskQueueMapper;

  private RouterService routerService;

  @BeforeEach
  void init() {
    routerService = new RouterService(mConfigRepository, mTaskQueueMapper);

    Mockito.when(mTaskQueueMapper.getTaskQueue(Geography.AUTO)).thenReturn(US_TASK_QUEUE);
    Mockito.when(mTaskQueueMapper.getTaskQueue(Geography.US)).thenReturn(US_TASK_QUEUE);
    Mockito.when(mTaskQueueMapper.getTaskQueue(Geography.EU)).thenReturn(EU_TASK_QUEUE);
  }

  @Test
  void testGetTaskQueue() throws IOException {
    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.AUTO);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID));

    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.US);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID));

    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.EU);
    assertEquals(EU_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID));
  }

}

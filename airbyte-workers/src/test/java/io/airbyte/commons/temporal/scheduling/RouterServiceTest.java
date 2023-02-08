/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mock.Strictness.LENIENT;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.config.Geography;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.util.HashSet;
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
  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private static final String US_TASK_QUEUE = "US_TASK_QUEUE";
  private static final String EU_TASK_QUEUE = "EU_TASK_QUEUE";

  @Mock(strictness = LENIENT)
  private ConfigRepository mConfigRepository;

  @Mock(strictness = LENIENT)
  private TaskQueueMapper mTaskQueueMapper;

  @Mock
  private FeatureFlags mockFeatureFlag;

  private RouterService routerService;

  @BeforeEach
  void init() {
    routerService = new RouterService(mConfigRepository, mTaskQueueMapper,
        mockFeatureFlag);

    Mockito.when(mTaskQueueMapper.getTaskQueue(eq(Geography.AUTO), any(TemporalJobType.class))).thenReturn(US_TASK_QUEUE);
    Mockito.when(mTaskQueueMapper.getTaskQueue(eq(Geography.US), any(TemporalJobType.class))).thenReturn(US_TASK_QUEUE);
    Mockito.when(mTaskQueueMapper.getTaskQueue(eq(Geography.EU), any(TemporalJobType.class))).thenReturn(EU_TASK_QUEUE);
  }

  @Test
  void testGetTaskQueue() throws IOException {
    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.AUTO);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID, TemporalJobType.SYNC));

    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.US);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID, TemporalJobType.SYNC));

    Mockito.when(mConfigRepository.getGeographyForConnection(CONNECTION_ID)).thenReturn(Geography.EU);
    assertEquals(EU_TASK_QUEUE, routerService.getTaskQueue(CONNECTION_ID, TemporalJobType.SYNC));
  }

  @Test
  void testGetWorkspaceTaskQueueWithEnabledFlag() throws IOException {
    Mockito.when(mockFeatureFlag.routeTaskQueueForWorkspaceEnabled()).thenReturn(true);
    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.AUTO);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));

    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.US);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));

    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.EU);
    assertEquals(EU_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));
  }

  @Test
  void testGetWorkspaceTaskQueueWithDisabledFlag() throws IOException {
    Mockito.when(mockFeatureFlag.routeTaskQueueForWorkspaceEnabled()).thenReturn(false);
    Mockito.when(mockFeatureFlag.routeTaskQueueForWorkspaceAllowList()).thenReturn(new HashSet<>());

    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.AUTO);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));

    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.US);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));

    Mockito.when(mConfigRepository.getGeographyForWorkspace(WORKSPACE_ID)).thenReturn(Geography.EU);
    assertEquals(US_TASK_QUEUE, routerService.getTaskQueueForWorkspace(WORKSPACE_ID, TemporalJobType.CHECK_CONNECTION));
  }

}

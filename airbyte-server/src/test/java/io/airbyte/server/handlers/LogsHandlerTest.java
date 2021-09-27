/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.LogType;
import io.airbyte.api.model.LogsRequestBody;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import java.io.File;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class LogsHandlerTest {

  @Test
  public void testServerLogs() {
    final Configs configs = mock(Configs.class);
    when(configs.getWorkspaceRoot()).thenReturn(Path.of("/workspace"));
    when(configs.getWorkerEnvironment()).thenReturn(WorkerEnvironment.DOCKER);

    final File expected = Path.of(String.format("/workspace/server/logs/%s", LogClientSingleton.LOG_FILENAME)).toFile();
    final File actual = new LogsHandler().getLogs(configs, new LogsRequestBody().logType(LogType.SERVER));

    assertEquals(expected, actual);
  }

  @Test
  public void testSchedulerLogs() {
    final Configs configs = mock(Configs.class);
    when(configs.getWorkspaceRoot()).thenReturn(Path.of("/workspace"));
    when(configs.getWorkerEnvironment()).thenReturn(WorkerEnvironment.DOCKER);

    final File expected = Path.of(String.format("/workspace/scheduler/logs/%s", LogClientSingleton.LOG_FILENAME)).toFile();
    final File actual = new LogsHandler().getLogs(configs, new LogsRequestBody().logType(LogType.SCHEDULER));

    assertEquals(expected, actual);
  }

}

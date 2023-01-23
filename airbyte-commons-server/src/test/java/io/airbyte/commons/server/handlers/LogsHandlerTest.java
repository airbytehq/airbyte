/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.LogType;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import java.io.File;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class LogsHandlerTest {

  @Test
  void testServerLogs() {
    final Configs configs = mock(Configs.class);
    when(configs.getWorkspaceRoot()).thenReturn(Path.of("/workspace"));
    when(configs.getWorkerEnvironment()).thenReturn(WorkerEnvironment.DOCKER);
    when(configs.getLogConfigs()).thenReturn(LogConfigs.EMPTY);

    final File expected = Path.of(String.format("/workspace/server/logs/%s", LogClientSingleton.LOG_FILENAME)).toFile();
    final File actual = new LogsHandler(configs).getLogs(new LogsRequestBody().logType(LogType.SERVER));

    assertEquals(expected, actual);
  }

  @Test
  void testSchedulerLogs() {
    final Configs configs = mock(Configs.class);
    when(configs.getWorkspaceRoot()).thenReturn(Path.of("/workspace"));
    when(configs.getWorkerEnvironment()).thenReturn(WorkerEnvironment.DOCKER);
    when(configs.getLogConfigs()).thenReturn(LogConfigs.EMPTY);

    final File expected = Path.of(String.format("/workspace/scheduler/logs/%s", LogClientSingleton.LOG_FILENAME)).toFile();
    final File actual = new LogsHandler(configs).getLogs(new LogsRequestBody().logType(LogType.SCHEDULER));

    assertEquals(expected, actual);
  }

}

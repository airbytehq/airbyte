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

package io.airbyte.server.handlers;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class ArchiveHandlerTest {

  private ConfigRepository configRepository;
  private ArchiveHandler archiveHandler;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    archiveHandler = new ArchiveHandler("test-version", configRepository, mock(JobPersistence.class), mock(FileTtlManager.class));
  }

  @Test
  void testEmptyMigration() throws JsonValidationException, IOException {
    archiveHandler.importData(archiveHandler.exportData());
    verify(configRepository, never()).writeStandardWorkspace(any());
    verify(configRepository, never()).writeStandardSource(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());
    verify(configRepository, never()).writeSourceConnection(any());
    verify(configRepository, never()).writeDestinationConnection(any());
    verify(configRepository, never()).writeStandardSync(any());
    verify(configRepository, never()).writeStandardSchedule(any());
  }

}

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

package io.airbyte.workers.protocols.singer;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.singer.SingerMessage;
import io.airbyte.workers.SingerSyncWorker;
import io.airbyte.workers.TestConfigHelpers;
import java.nio.file.Path;
import java.util.Optional;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;

class SingerSyncWorkerTest {

  private static final Path WORKSPACE_ROOT = Path.of("/workspaces/10");
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  @SuppressWarnings("unchecked")
  @Test
  public void test() throws Exception {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    final StandardSync standardSync = syncPair.getKey();
    final StandardSyncInput syncInput = syncPair.getValue();

    final StandardTapConfig tapConfig = new StandardTapConfig()
        .withStandardSync(standardSync)
        .withSourceConnectionImplementation(syncInput.getSourceConnectionImplementation())
        .withState(syncInput.getState());

    final StandardTargetConfig targetConfig = new StandardTargetConfig()
        .withStandardSync(standardSync)
        .withDestinationConnectionImplementation(syncInput.getDestinationConnectionImplementation());

    final SingerTap tap = mock(DefaultSingerTap.class);
    final SingerTarget target = mock(DefaultSingerTarget.class);

    SingerMessage recordMessage1 = SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
    SingerMessage recordMessage2 = SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow");

    when(tap.isFinished()).thenReturn(false, false, false, true);
    when(tap.attemptRead()).thenReturn(Optional.of(recordMessage1), Optional.empty(), Optional.of(recordMessage2));

    final SingerSyncWorker singerSyncWorker = new SingerSyncWorker(tap, target);

    singerSyncWorker.run(syncInput, WORKSPACE_ROOT);

    verify(tap).start(tapConfig, WORKSPACE_ROOT);
    verify(target).start(targetConfig, WORKSPACE_ROOT);
    verify(target).accept(recordMessage1);
    verify(target).accept(recordMessage2);
    verify(tap).close();
    verify(target).close();
  }

}

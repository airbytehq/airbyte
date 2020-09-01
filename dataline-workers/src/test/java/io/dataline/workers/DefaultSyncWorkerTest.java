/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers;

import static org.mockito.Mockito.*;

import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import io.dataline.workers.protocol.singer.MessageUtils;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;

class DefaultSyncWorkerTest extends BaseWorkerTestCase {

  private static final Path WORKSPACE_ROOT = Path.of("/workspaces/10");
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";
  private static final long LAST_SYNC_TIME = 1598565106;

  @SuppressWarnings("unchecked")
  @Test
  public void test() throws Exception {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair =
        TestConfigHelpers.createSyncConfig();
    final StandardSync standardSync = syncPair.getKey();
    final StandardSyncInput syncInput = syncPair.getValue();

    final StandardSyncSummary syncSummary = new StandardSyncSummary();
    syncSummary.setStatus(StandardSyncSummary.Status.COMPLETED);
    syncSummary.setRecordsSynced(10L);
    syncSummary.setStatus(StandardSyncSummary.Status.COMPLETED);
    syncSummary.setStartTime(LAST_SYNC_TIME);
    syncSummary.setEndTime(LAST_SYNC_TIME);

    final StandardTapConfig tapConfig = new StandardTapConfig();
    tapConfig.setStandardSync(standardSync);
    tapConfig.setSourceConnectionImplementation(syncInput.getSourceConnectionImplementation());
    tapConfig.setState(syncInput.getState());

    final StandardTargetConfig targetConfig = new StandardTargetConfig();
    targetConfig.setStandardSync(standardSync);
    targetConfig.setDestinationConnectionImplementation(
        syncInput.getDestinationConnectionImplementation());

    final TapFactory<SingerMessage> tapFactory = (TapFactory<SingerMessage>) mock(TapFactory.class);
    final TargetFactory<SingerMessage> targetFactory =
        (TargetFactory<SingerMessage>) mock(TargetFactory.class);
    final CloseableConsumer<SingerMessage> consumer =
        (CloseableConsumer<SingerMessage>) mock(CloseableConsumer.class);

    SingerMessage recordMessage1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    SingerMessage recordMessage2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final Stream<SingerMessage> tapStream = spy(Stream.of(recordMessage1, recordMessage2));

    when(tapFactory.create(tapConfig, WORKSPACE_ROOT)).thenReturn(tapStream);
    when(targetFactory.create(targetConfig, WORKSPACE_ROOT)).thenReturn(consumer);
    final DefaultSyncWorker defaultSyncWorker = new DefaultSyncWorker(tapFactory, targetFactory);

    defaultSyncWorker.run(syncInput, WORKSPACE_ROOT);

    verify(tapFactory).create(tapConfig, WORKSPACE_ROOT);
    verify(targetFactory).create(targetConfig, WORKSPACE_ROOT);
    verify(tapStream).close();
    verify(consumer).accept(recordMessage1);
    verify(consumer).accept(recordMessage2);
    verify(consumer).close();
  }

}

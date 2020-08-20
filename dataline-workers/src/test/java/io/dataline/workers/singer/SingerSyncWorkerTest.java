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

package io.dataline.workers.singer;

import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.PostgreSQLContainerHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Set;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class SingerSyncWorkerTest extends BaseWorkerTestCase {

  @Test
  public void testIt() throws IOException, SQLException, InterruptedException {
    PostgreSQLContainer sourceDb = new PostgreSQLContainer();

    sourceDb.start();
    sourceDb.copyFileToContainer(
        MountableFile.forClasspathResource("simple_postgres_init.sql"), "/etc/init.sql");
    sourceDb.execInContainer(
        "psql",
        "-d",
        sourceDb.getDatabaseName(),
        "-U",
        sourceDb.getUsername(),
        "-a",
        "-f",
        "/etc/init.sql");
    PostgreSQLContainer targetDb = new PostgreSQLContainer();
    targetDb.start();

    String tapConfig = PostgreSQLContainerHelper.getSingerConfigJson(sourceDb);
    String targetConfig = PostgreSQLContainerHelper.getSingerConfigJson(targetDb);

    Set<String> expectedTables = PostgreSQLContainerHelper.getTables(sourceDb);

    new SingerSyncWorker(
            "1",
            getWorkspacePath().toAbsolutePath().toString(),
            SINGER_LIB_PATH,
            SingerTap.POSTGRES,
            tapConfig,
            readResource("simple_postgres_sync_catalog.json"),
            "{}", // fresh sync, no state
            SingerTarget.POSTGRES,
            targetConfig)
        .run();

    Set<String> actualTables = PostgreSQLContainerHelper.getTables(targetDb);
    Assertions.assertEquals(expectedTables, actualTables);
  }
}

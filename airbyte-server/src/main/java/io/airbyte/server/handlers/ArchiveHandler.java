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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.ConfigDumpExporter;
import io.airbyte.server.ConfigDumpImporter;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ArchiveHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ArchiveHandler.class);

  public static final Path SEEDS_PATH = Path.of(System.getProperty("user.dir")).resolve("latest_seeds");

  private final String version;
  private final ConfigRepository configRepository;
  private final ConfigDumpExporter configDumpExporter;
  private final ConfigDumpImporter configDumpImporter;
  private final FileTtlManager fileTtlManager;

  public ArchiveHandler(final String version,
                        final ConfigRepository configRepository,
                        final JobPersistence jobPersistence,
                        final FileTtlManager fileTtlManager) {
    this(
        version,
        configRepository,
        fileTtlManager,
        new ConfigDumpExporter(configRepository, jobPersistence),
        new ConfigDumpImporter(configRepository, jobPersistence));
  }

  @VisibleForTesting
  ArchiveHandler(final String version,
                 final ConfigRepository configRepository,
                 final FileTtlManager fileTtlManager,
                 final ConfigDumpExporter configDumpExporter,
                 final ConfigDumpImporter configDumpImporter) {
    this.version = version;
    this.configRepository = configRepository;
    this.configDumpExporter = configDumpExporter;
    this.configDumpImporter = configDumpImporter;
    this.fileTtlManager = fileTtlManager;
  }

  /**
   * Creates an archive tarball file using Gzip compression of internal Airbyte Data and
   *
   * @return that tarball File.
   */
  public File exportData() {
    final File archive = configDumpExporter.dump();
    fileTtlManager.register(archive.toPath());
    return archive;
  }

  /**
   * Extract internal Airbyte data from the @param archive tarball file (using Gzip compression) as
   * produced by {@link #exportData()}. Note that the provided archived file will be deleted.
   *
   * @return a status object describing if import was successful or not.
   */
  public ImportRead importData(File archive) {
    ImportRead result;
    try {
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
      try {
        configDumpImporter.importDataWithSeed(version, archive, SEEDS_PATH);
        result = new ImportRead().status(StatusEnum.SUCCEEDED);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
        FileUtils.deleteQuietly(archive);
      }
    } catch (Exception e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

}

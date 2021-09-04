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

import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.api.model.ImportRequestBody;
import io.airbyte.api.model.UploadRead;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.YamlSeedConfigPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.ConfigDumpExporter;
import io.airbyte.server.ConfigDumpImporter;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ArchiveHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ArchiveHandler.class);

  private final String version;
  private final ConfigDumpExporter configDumpExporter;
  private final ConfigDumpImporter configDumpImporter;
  private final FileTtlManager fileTtlManager;

  public ArchiveHandler(final String version,
                        final ConfigRepository configRepository,
                        final JobPersistence jobPersistence,
                        final WorkspaceHelper workspaceHelper,
                        final FileTtlManager fileTtlManager) {
    this(
        version,
        fileTtlManager,
        new ConfigDumpExporter(configRepository, jobPersistence, workspaceHelper),
        new ConfigDumpImporter(configRepository, jobPersistence, workspaceHelper));
  }

  public ArchiveHandler(final String version,
                        final FileTtlManager fileTtlManager,
                        final ConfigDumpExporter configDumpExporter,
                        final ConfigDumpImporter configDumpImporter) {
    this.version = version;
    this.configDumpExporter = configDumpExporter;
    this.configDumpImporter = configDumpImporter;
    this.fileTtlManager = fileTtlManager;
  }

  /**
   * Creates an archive tarball file using Gzip compression of internal Airbyte Data
   *
   * @return that tarball File.
   */
  public File exportData() {
    final File archive = configDumpExporter.dump();
    fileTtlManager.register(archive.toPath());
    return archive;
  }

  /**
   * Creates an archive tarball file using Gzip compression of only configurations tied to
   *
   * @param workspaceIdRequestBody which is the target workspace to export
   * @return that lightweight tarball file
   */
  public File exportWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {
    final File archive;
    try {
      archive = configDumpExporter.exportWorkspace(workspaceIdRequestBody.getWorkspaceId());
      fileTtlManager.register(archive.toPath());
      return archive;
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new InternalServerKnownException(String.format("Failed to export Workspace configuration due to: %s", e.getMessage()));
    }
  }

  /**
   * Extract internal Airbyte data from the @param archive tarball file (using Gzip compression) as
   * produced by {@link #exportData()}. Note that the provided archived file will be deleted.
   *
   * @return a status object describing if import was successful or not.
   */
  public ImportRead importData(File archive) {
    try {
      return importInternal(() -> configDumpImporter.importDataWithSeed(version, archive, YamlSeedConfigPersistence.get()));
    } finally {
      FileUtils.deleteQuietly(archive);
    }
  }

  public UploadRead uploadArchiveResource(File archive) {
    return configDumpImporter.uploadArchiveResource(archive);
  }

  /**
   * Extract Airbyte configuration data from the archive tarball file (using Gzip compression) as
   * produced by {@link #exportWorkspace(WorkspaceIdRequestBody)}. The configurations from the tarball
   * may get mutated to be safely included into the current workspace. (the exact same tarball could
   * be imported into 2 different workspaces) Note that the provided archived file will be deleted.
   *
   * @return a status object describing if import was successful or not.
   */
  public ImportRead importIntoWorkspace(ImportRequestBody importRequestBody) {
    final File archive = configDumpImporter.getArchiveResource(importRequestBody.getResourceId());
    try {
      return importInternal(
          () -> configDumpImporter.importIntoWorkspace(version, importRequestBody.getWorkspaceId(), archive));
    } finally {
      configDumpImporter.deleteArchiveResource(importRequestBody.getResourceId());
    }
  }

  private ImportRead importInternal(importCall importCall) {
    ImportRead result;
    try {
      importCall.importData();
      result = new ImportRead().status(StatusEnum.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

  public interface importCall {

    void importData() throws IOException, JsonValidationException, ConfigNotFoundException;

  }

}

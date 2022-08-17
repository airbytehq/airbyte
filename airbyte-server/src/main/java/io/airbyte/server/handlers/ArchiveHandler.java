/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.ImportRead;
import io.airbyte.api.model.generated.ImportRead.StatusEnum;
import io.airbyte.api.model.generated.ImportRequestBody;
import io.airbyte.api.model.generated.UploadRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
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

  private final AirbyteVersion version;
  private final ConfigDumpExporter configDumpExporter;
  private final ConfigDumpImporter configDumpImporter;
  private final ConfigPersistence seed;
  private final FileTtlManager fileTtlManager;

  public ArchiveHandler(final AirbyteVersion version,
                        final ConfigRepository configRepository,
                        final SecretsRepositoryReader secretsRepositoryReader,
                        final SecretsRepositoryWriter secretsRepositoryWriter,
                        final JobPersistence jobPersistence,
                        final ConfigPersistence seed,
                        final WorkspaceHelper workspaceHelper,
                        final FileTtlManager fileTtlManager,
                        final boolean importDefinitions) {
    this(
        version,
        fileTtlManager,
        new ConfigDumpExporter(configRepository, secretsRepositoryReader, jobPersistence, workspaceHelper),
        new ConfigDumpImporter(configRepository, secretsRepositoryWriter, jobPersistence, workspaceHelper, importDefinitions),
        seed);
  }

  public ArchiveHandler(final AirbyteVersion version,
                        final FileTtlManager fileTtlManager,
                        final ConfigDumpExporter configDumpExporter,
                        final ConfigDumpImporter configDumpImporter,
                        final ConfigPersistence seed) {
    this.version = version;
    this.configDumpExporter = configDumpExporter;
    this.configDumpImporter = configDumpImporter;
    this.seed = seed;
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
  public File exportWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    final File archive;
    try {
      archive = configDumpExporter.exportWorkspace(workspaceIdRequestBody.getWorkspaceId());
      fileTtlManager.register(archive.toPath());
      return archive;
    } catch (final JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new InternalServerKnownException(String.format("Failed to export Workspace configuration due to: %s", e.getMessage()), e);
    }
  }

  /**
   * Extract internal Airbyte data from the @param archive tarball file (using Gzip compression) as
   * produced by {@link #exportData()}. Note that the provided archived file will be deleted.
   *
   * @return a status object describing if import was successful or not.
   */
  public ImportRead importData(final File archive) {
    try {
      return importInternal(() -> configDumpImporter.importDataWithSeed(version, archive, seed));
    } finally {
      FileUtils.deleteQuietly(archive);
    }
  }

  public UploadRead uploadArchiveResource(final File archive) {
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
  public ImportRead importIntoWorkspace(final ImportRequestBody importRequestBody) {
    final File archive = configDumpImporter.getArchiveResource(importRequestBody.getResourceId());
    try {
      return importInternal(
          () -> configDumpImporter.importIntoWorkspace(version, importRequestBody.getWorkspaceId(), archive));
    } finally {
      configDumpImporter.deleteArchiveResource(importRequestBody.getResourceId());
    }
  }

  private ImportRead importInternal(final importCall importCall) {
    ImportRead result;
    try {
      importCall.importData();
      result = new ImportRead().status(StatusEnum.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

  public interface importCall {

    void importData() throws IOException, JsonValidationException, ConfigNotFoundException;

  }

  public boolean canImportDefinitions() {
    return configDumpImporter.canImportDefinitions();
  }

}

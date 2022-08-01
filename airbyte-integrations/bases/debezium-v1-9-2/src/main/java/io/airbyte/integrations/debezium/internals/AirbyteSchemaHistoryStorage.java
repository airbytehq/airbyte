/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.debezium.document.Document;
import io.debezium.document.DocumentReader;
import io.debezium.document.DocumentWriter;
import io.debezium.relational.history.HistoryRecord;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Optional;
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;

/**
 * The purpose of this class is : to , 1. Read the contents of the file {@link #path} which contains
 * the schema history at the end of the sync so that it can be saved in state for future syncs.
 * Check {@link #read()} 2. Write the saved content back to the file {@link #path} at the beginning
 * of the sync so that debezium can function smoothly. Check persist(Optional&lt;JsonNode&gt;). To
 * understand more about file, please refer {@link FilteredFileDatabaseHistory}
 */
public class AirbyteSchemaHistoryStorage {

  private final Path path;
  private static final Charset UTF8 = StandardCharsets.UTF_8;
  private final DocumentReader reader = DocumentReader.defaultReader();
  private final DocumentWriter writer = DocumentWriter.defaultWriter();

  public AirbyteSchemaHistoryStorage(final Path path) {
    this.path = path;
  }

  public Path getPath() {
    return path;
  }

  /**
   * This implementation is kind of similar to
   * {@link io.debezium.relational.history.FileDatabaseHistory#recoverRecords(Consumer)}
   */
  public String read() {
    final StringBuilder fileAsString = new StringBuilder();
    try {
      for (final String line : Files.readAllLines(path, UTF8)) {
        if (line != null && !line.isEmpty()) {
          final Document record = reader.read(line);
          final String recordAsString = writer.write(record);
          fileAsString.append(recordAsString);
          fileAsString.append(System.lineSeparator());
        }
      }
      return fileAsString.toString();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * This implementation is kind of similar to
   * {@link io.debezium.relational.history.FileDatabaseHistory#start()}
   */
  private void makeSureFileExists() {
    try {
      // Make sure the file exists ...
      if (!Files.exists(path)) {
        // Create parent directories if we have them ...
        if (path.getParent() != null) {
          Files.createDirectories(path.getParent());
        }
        try {
          Files.createFile(path);
        } catch (final FileAlreadyExistsException e) {
          // do nothing
        }
      }
    } catch (final IOException e) {
      throw new IllegalStateException(
          "Unable to check or create history file at " + path + ": " + e.getMessage(), e);
    }
  }

  public void persist(final Optional<JsonNode> schemaHistory) {
    if (schemaHistory.isEmpty()) {
      return;
    }
    final String fileAsString = Jsons.object(schemaHistory.get(), String.class);

    if (fileAsString == null || fileAsString.isEmpty()) {
      return;
    }

    FileUtils.deleteQuietly(path.toFile());
    makeSureFileExists();
    writeToFile(fileAsString);
  }

  /**
   * This implementation is kind of similar to
   * {@link io.debezium.relational.history.FileDatabaseHistory#storeRecord(HistoryRecord)}
   *
   * @param fileAsString Represents the contents of the file saved in state from previous syncs
   */
  private void writeToFile(final String fileAsString) {
    try {
      final String[] split = fileAsString.split(System.lineSeparator());
      for (final String element : split) {
        final Document read = reader.read(element);
        final String line = writer.write(read);

        try (final BufferedWriter historyWriter = Files
            .newBufferedWriter(path, StandardOpenOption.APPEND)) {
          try {
            historyWriter.append(line);
            historyWriter.newLine();
          } catch (final IOException e) {
            throw new RuntimeException(e);
          }
        }
      }
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static AirbyteSchemaHistoryStorage initializeDBHistory(final Optional<JsonNode> schemaHistory) {
    final Path dbHistoryWorkingDir;
    try {
      dbHistoryWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-db-history");
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    final Path dbHistoryFilePath = dbHistoryWorkingDir.resolve("dbhistory.dat");

    final AirbyteSchemaHistoryStorage schemaHistoryManager = new AirbyteSchemaHistoryStorage(dbHistoryFilePath);
    schemaHistoryManager.persist(schemaHistory);
    return schemaHistoryManager;
  }

}

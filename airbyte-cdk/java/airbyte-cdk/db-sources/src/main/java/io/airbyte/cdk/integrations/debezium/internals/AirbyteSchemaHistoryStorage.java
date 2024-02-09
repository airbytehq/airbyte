/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.debezium.document.Document;
import io.debezium.document.DocumentReader;
import io.debezium.document.DocumentWriter;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Optional;
import java.util.Properties;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The purpose of this class is : to , 1. Read the contents of the file {@link #path} which contains
 * the schema history at the end of the sync so that it can be saved in state for future syncs.
 * Check {@link #read()} 2. Write the saved content back to the file {@link #path} at the beginning
 * of the sync so that debezium can function smoothly. Check persist(Optional&lt;JsonNode&gt;).
 */
public class AirbyteSchemaHistoryStorage {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteSchemaHistoryStorage.class);
  private static final long SIZE_LIMIT_TO_COMPRESS_MB = 3;
  public static final int ONE_MB = 1024 * 1024;
  private static final Charset UTF8 = StandardCharsets.UTF_8;

  private final DocumentReader reader = DocumentReader.defaultReader();
  private final DocumentWriter writer = DocumentWriter.defaultWriter();
  private final Path path;
  private final boolean compressSchemaHistoryForState;

  public AirbyteSchemaHistoryStorage(final Path path, final boolean compressSchemaHistoryForState) {
    this.path = path;
    this.compressSchemaHistoryForState = compressSchemaHistoryForState;
  }

  public record SchemaHistory<T> (T schema, boolean isCompressed) {}

  public SchemaHistory<String> read() {
    final double fileSizeMB = (double) path.toFile().length() / (ONE_MB);
    if ((fileSizeMB > SIZE_LIMIT_TO_COMPRESS_MB) && compressSchemaHistoryForState) {
      LOGGER.info("File Size {} MB is greater than the size limit of {} MB, compressing the content of the file.", fileSizeMB,
          SIZE_LIMIT_TO_COMPRESS_MB);
      final String schemaHistory = readCompressed();
      final double compressedSizeMB = calculateSizeOfStringInMB(schemaHistory);
      if (fileSizeMB > compressedSizeMB) {
        LOGGER.info("Content Size post compression is {} MB ", compressedSizeMB);
      } else {
        throw new RuntimeException("Compressing increased the size of the content. Size before compression " + fileSizeMB + ", after compression "
            + compressedSizeMB);
      }
      return new SchemaHistory<>(schemaHistory, true);
    }
    if (compressSchemaHistoryForState) {
      LOGGER.info("File Size {} MB is less than the size limit of {} MB, reading the content of the file without compression.", fileSizeMB,
          SIZE_LIMIT_TO_COMPRESS_MB);
    } else {
      LOGGER.info("File Size {} MB.", fileSizeMB);
    }
    final String schemaHistory = readUncompressed();
    return new SchemaHistory<>(schemaHistory, false);
  }

  @VisibleForTesting
  public String readUncompressed() {
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

  private String readCompressed() {
    final String lineSeparator = System.lineSeparator();
    final ByteArrayOutputStream compressedStream = new ByteArrayOutputStream();
    try (final GZIPOutputStream gzipOutputStream = new GZIPOutputStream(compressedStream);
        final BufferedReader bufferedReader = Files.newBufferedReader(path, UTF8)) {
      for (;;) {
        final String line = bufferedReader.readLine();
        if (line == null) {
          break;
        }

        if (!line.isEmpty()) {
          final Document record = reader.read(line);
          final String recordAsString = writer.write(record);
          gzipOutputStream.write(recordAsString.getBytes(StandardCharsets.UTF_8));
          gzipOutputStream.write(lineSeparator.getBytes(StandardCharsets.UTF_8));
        }
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return Jsons.serialize(compressedStream.toByteArray());
  }

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

  private void persist(final SchemaHistory<Optional<JsonNode>> schemaHistory) {
    if (schemaHistory.schema().isEmpty()) {
      return;
    }
    final String fileAsString = Jsons.object(schemaHistory.schema().get(), String.class);

    if (fileAsString == null || fileAsString.isEmpty()) {
      return;
    }

    FileUtils.deleteQuietly(path.toFile());
    makeSureFileExists();
    if (schemaHistory.isCompressed()) {
      writeCompressedStringToFile(fileAsString);
    } else {
      writeToFile(fileAsString);
    }
  }

  /**
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

  private void writeCompressedStringToFile(final String compressedString) {
    try (final ByteArrayInputStream inputStream = new ByteArrayInputStream(Jsons.deserialize(compressedString, byte[].class));
        final GZIPInputStream gzipInputStream = new GZIPInputStream(inputStream);
        final FileOutputStream fileOutputStream = new FileOutputStream(path.toFile())) {
      final byte[] buffer = new byte[1024];
      int bytesRead;
      while ((bytesRead = gzipInputStream.read(buffer)) != -1) {
        fileOutputStream.write(buffer, 0, bytesRead);
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @VisibleForTesting
  public static double calculateSizeOfStringInMB(final String string) {
    return (double) string.getBytes(StandardCharsets.UTF_8).length / (ONE_MB);
  }

  public static AirbyteSchemaHistoryStorage initializeDBHistory(final SchemaHistory<Optional<JsonNode>> schemaHistory,
                                                                final boolean compressSchemaHistoryForState) {
    final Path dbHistoryWorkingDir;
    try {
      dbHistoryWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-db-history");
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    final Path dbHistoryFilePath = dbHistoryWorkingDir.resolve("dbhistory.dat");

    final AirbyteSchemaHistoryStorage schemaHistoryManager =
        new AirbyteSchemaHistoryStorage(dbHistoryFilePath, compressSchemaHistoryForState);
    schemaHistoryManager.persist(schemaHistory);
    return schemaHistoryManager;
  }

  public void setDebeziumProperties(Properties props) {
    // https://debezium.io/documentation/reference/2.2/operations/debezium-server.html#debezium-source-database-history-class
    // https://debezium.io/documentation/reference/development/engine.html#_in_the_code
    // As mentioned in the documents above, debezium connector for MySQL needs to track the schema
    // changes. If we don't do this, we can't fetch records for the table.
    props.setProperty("schema.history.internal", "io.debezium.storage.file.history.FileSchemaHistory");
    props.setProperty("schema.history.internal.file.filename", path.toString());
    props.setProperty("schema.history.internal.store.only.captured.databases.ddl", "true");
  }

}

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

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_DB_HISTORY;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.StateManager;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
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
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;

/**
 * The purpose of this class is : to , 1. Read the contents of the file {@link #path} at the end of
 * the sync so that it can be saved in state for future syncs. Check {@link #read()} 2. Write the
 * saved content back to the file {@link #path} at the beginning of the sync so that debezium can
 * function smoothly. Check {@link #persist(CdcState)}. To understand more about file, please refer
 * {@link FilteredFileDatabaseHistory}
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
   * This implementation is is kind of similar to
   * {@link io.debezium.relational.history.FileDatabaseHistory#recoverRecords(Consumer)}
   */
  public String read() {
    StringBuilder fileAsString = new StringBuilder();
    try {
      for (String line : Files.readAllLines(path, UTF8)) {
        if (line != null && !line.isEmpty()) {
          Document record = reader.read(line);
          String recordAsString = writer.write(record);
          fileAsString.append(recordAsString);
          fileAsString.append(System.lineSeparator());
        }
      }
      return fileAsString.toString();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * This implementation is is kind of similar to
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
        } catch (FileAlreadyExistsException e) {
          // do nothing
        }
      }
    } catch (IOException e) {
      throw new IllegalStateException(
          "Unable to create history file at " + path + ": " + e.getMessage(), e);
    }
  }

  public void persist(CdcState cdcState) {
    String fileAsString = cdcState != null && cdcState.getState() != null ? Jsons
        .object(cdcState.getState().get(MYSQL_DB_HISTORY), String.class) : null;

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
  private void writeToFile(String fileAsString) {
    try {
      String[] split = fileAsString.split(System.lineSeparator());
      for (String element : split) {
        Document read = reader.read(element);
        String line = writer.write(read);

        try (BufferedWriter historyWriter = Files
            .newBufferedWriter(path, StandardOpenOption.APPEND)) {
          try {
            historyWriter.append(line);
            historyWriter.newLine();
          } catch (IOException e) {
            throw new RuntimeException(e);
          }
        }
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  static AirbyteSchemaHistoryStorage initializeDBHistory(StateManager stateManager) {
    final Path dbHistoryWorkingDir;
    try {
      dbHistoryWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-db-history");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    final Path dbHistoryFilePath = dbHistoryWorkingDir.resolve("dbhistory.dat");

    final AirbyteSchemaHistoryStorage schemaHistoryManager = new AirbyteSchemaHistoryStorage(dbHistoryFilePath);
    schemaHistoryManager.persist(stateManager.getCdcStateManager().getCdcState());
    return schemaHistoryManager;
  }

}

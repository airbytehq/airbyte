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

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.scheduler.persistence.DatabaseSchema;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseArchiver.class);
  private static final String DB_FOLDER_NAME = "airbyte_db";

  private final JobPersistence persistence;
  private final Path storageRoot;
  private final JsonSchemaValidator jsonSchemaValidator;

  public DatabaseArchiver(final JobPersistence persistence, final Path storageRoot, final JsonSchemaValidator jsonSchemaValidator) {
    this.persistence = persistence;
    this.storageRoot = storageRoot;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public DatabaseArchiver(final JobPersistence persistence, final Path storageRoot) {
    this(persistence, storageRoot, new JsonSchemaValidator());
  }

  /**
   * Serializes each internal Airbyte Database table into a single archive file stored in YAML.
   */
  public void writeDatabaseToArchive() throws IOException {
    final Map<String, Stream<JsonNode>> tables = persistence.exportDatabase();
    if (tables != null && !tables.isEmpty()) {
      tables.forEach((tableName, tableStream) -> Exceptions.toRuntime(() -> writeTableToArchive(tableName, tableStream)));
      LOGGER.debug("Successful export of airbyte database");
    }
  }

  private void writeTableToArchive(final String tableName, final Stream<JsonNode> tableStream) throws Exception {
    final JsonNode schema = DatabaseSchema.forTable(tableName);
    if (schema != null) {
      final Path tablePath = buildTablePath(tableName);
      Files.createDirectories(tablePath.getParent());
      final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(tablePath.toFile()));
      final CloseableConsumer<JsonNode> recordConsumer = Yamls.listWriter(recordOutputWriter);
      tableStream.forEach(row -> Exceptions.toRuntime(() -> {
        jsonSchemaValidator.ensure(schema, row);
        recordConsumer.accept(row);
      }));
      recordConsumer.close();
      LOGGER.debug(String.format("Successful export of airbyte table %s", tableName));
    } else {
      throw new IllegalArgumentException(String.format("Unable to locate schema definition for table %s", tableName));
    }
  }

  private Path buildTablePath(final String tableName) {
    return storageRoot
        .resolve(DB_FOLDER_NAME)
        .resolve(String.format("%s.yaml", tableName.toLowerCase()));
  }

  /**
   * Reads a YAML configuration archive file and deserialize table into the Airbyte Database. The
   * objects will be validated against the current version of Airbyte server's JSON Schema.
   */
  public void readDatabaseFromArchive() throws IOException {
    final Path dbFolder = storageRoot.resolve(DB_FOLDER_NAME);
    if (dbFolder.toFile().exists()) {
      try (final Stream<Path> files = Files.walk(dbFolder)) {
        final Map<String, Stream<JsonNode>> data = files
            .filter(f -> Files.isRegularFile(f) && f.toString().endsWith(".yaml"))
            .collect(Collectors.toMap(f -> f.getFileName().toString().replace(".yaml", ""), this::readTableFromArchive));
        persistence.importDatabase(data);
      }
      LOGGER.debug("Successful read of airbyte database from archive");
    } else {
      LOGGER.debug("Airbyte Database was not found in the archive");
    }
  }

  private Stream<JsonNode> readTableFromArchive(final Path tablePath) {
    final String tableName = tablePath.getFileName().toString().replace(".yaml", "");
    final JsonNode schema = DatabaseSchema.forTable(tableName);
    if (schema != null) {
      return MoreStreams.toStream(Yamls.deserialize(IOs.readFile(tablePath)).elements())
          .peek(r -> {
            try {
              jsonSchemaValidator.ensure(schema, r);
            } catch (JsonValidationException e) {
              throw new IllegalArgumentException("Archived Data Schema does not match current Airbyte Data Schemas", e);
            }
          });
    } else {
      throw new IllegalArgumentException(String.format("Unable to locate schema definition for table %s", tableName));
    }
  }

}

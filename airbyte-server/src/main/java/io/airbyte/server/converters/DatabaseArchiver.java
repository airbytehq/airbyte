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
import java.util.List;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseArchiver.class);
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String BACKUP_SCHEMA = "import_backup";
  private static final String DEFAULT_SCHEMA = "public";

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
    List<String> tables = persistence.listTables(DEFAULT_SCHEMA);
    if (tables != null) {
      tables.forEach(tableName -> Exceptions.toRuntime(() -> writeTableToArchive(tableName)));
      LOGGER.debug("Successful export of airbyte database");
    }
  }

  private void writeTableToArchive(final String tableName) throws Exception {
    final JsonNode schema = DatabaseSchema.forTable(tableName);
    if (schema != null) {
      final Path tablePath = buildTablePath(tableName);
      Files.createDirectories(tablePath.getParent());
      final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(tablePath.toFile()));
      final CloseableConsumer<JsonNode> recordConsumer = Yamls.listWriter(recordOutputWriter);
      persistence.serialize(tableName).forEach(row -> Exceptions.toRuntime(() -> {
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
  public void readDatabaseFromArchive(final String tempSchema) throws IOException {
    if (storageRoot.resolve(DB_FOLDER_NAME).toFile().exists()) {
      Files.walk(storageRoot.resolve(DB_FOLDER_NAME))
          .filter(f -> Files.isRegularFile(f) && f.endsWith(".yaml"))
          .forEach(table -> Exceptions.toRuntime(() -> readTableFromArchive(table, tempSchema)));
      LOGGER.debug("Successful read of airbyte database from archive");
    } else {
      LOGGER.debug("Airbyte Database was not found in the archive");
    }
  }

  private void readTableFromArchive(final Path tablePath, final String tempSchema) throws IOException {
    final String tableName = tablePath.getFileName().toString();
    final JsonNode schema = DatabaseSchema.forTable(tableName);
    if (schema != null) {
      final Stream<JsonNode> recordStream = MoreStreams.toStream(Yamls.deserialize(IOs.readFile(tablePath)).elements())
          .peek(r -> {
            try {
              jsonSchemaValidator.ensure(schema, r);
            } catch (JsonValidationException e) {
              throw new IllegalArgumentException("Archived Data Schema does not match current Airbyte Data Schemas", e);
            }
          });
      final String tableSQL = String.format("%s.%s", tempSchema, tableName);
      persistence.deserialize(tableSQL, schema, recordStream);
      LOGGER.debug(String.format("Successful read of airbyte table %s", tableName));
    } else {
      throw new IllegalArgumentException(String.format("Unable to locate schema definition for table %s", tableName));
    }
  }

  public boolean checkDatabase(final String tempSchema) throws IOException {
    // Add sanity checks on the database in tempSchema here
    // left empty for the moment
    LOGGER.debug("Successful test of staged airbyte database");
    return !persistence.listTables(tempSchema).isEmpty();
  }

  public void commitDatabase(final String tempSchema) throws IOException {
    persistence.dropSchema(BACKUP_SCHEMA);
    persistence.swapSchema(tempSchema, DEFAULT_SCHEMA, BACKUP_SCHEMA);
    LOGGER.debug("Successful import of airbyte database");
  }

  public void dropSchema(String tempSchema) throws IOException {
    persistence.dropSchema(tempSchema);
  }

}

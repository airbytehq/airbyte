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
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.Record;
import org.jooq.Table;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseArchiver.class);
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String DEFAULT_SCHEMA = "public";
  private static final JSONFormat DB_JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private final ExceptionWrappingDatabase database;
  private final Path storageRoot;
  private final JsonSchemaValidator jsonSchemaValidator;

  public DatabaseArchiver(final Database database, final Path storageRoot, final JsonSchemaValidator jsonSchemaValidator) {
    this.database = new ExceptionWrappingDatabase(database);
    this.storageRoot = storageRoot;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public DatabaseArchiver(final Database database, final Path storageRoot) {
    this(database, storageRoot, new JsonSchemaValidator());
  }

  /**
   * Serializes each internal Airbyte Database table into a single archive file stored in YAML.
   */
  public void writeDatabaseToArchive() throws IOException {
    List<Table<?>> tables = listTables();
    if (tables != null) {
      tables.forEach(table -> Exceptions.toRuntime(() -> writeTableToArchive(table)));
    }
    LOGGER.debug("Successful export of airbyte database");
  }

  private List<Table<?>> listTables() throws IOException {
    // list tables from public schema only
    return database.query(context -> context.meta().getSchemas(DEFAULT_SCHEMA).stream()
        .flatMap(schema -> context.meta(schema).getTables().stream())
        .collect(Collectors.toList()));
  }

  private void writeTableToArchive(Table<?> table) throws Exception {
    final Path tablePath = buildTablePath(table.getName());
    Files.createDirectories(tablePath.getParent());
    final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(tablePath.toFile()));
    final CloseableConsumer<JsonNode> recordConsumer = Yamls.listWriter(recordOutputWriter);
    final Stream<Record> records = database.query(ctx -> ctx.select(table.fields())
        .from(table.getName())
        .fetchStream());
    records.forEach(r -> Exceptions.toRuntime(() -> {
      final JsonNode row = Jsons.deserialize(r.formatJSON(DB_JSON_FORMAT));
      // TODO validate table schemas before writing?
      recordConsumer.accept(row);
    }));
    recordConsumer.close();
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
  public String readDatabaseFromArchive() throws IOException, JsonValidationException {
    final String tempSchema = "tempSchema";
    // TODO implement to a temp schema
    LOGGER.debug("Successful read of airbyte database");
    return tempSchema;
  }

  public boolean checkDatabase(final String tempSchema) {
    // TODO implement
    LOGGER.debug("Successful test of staged airbyte database");
    return true;
  }

  public void commitDatabase(final String tempSchema) {
    // TODO implement
    LOGGER.debug("Successful import of airbyte database");
  }

  public void dropSchema(String tempSchema) {
    // TODO implement
  }

}

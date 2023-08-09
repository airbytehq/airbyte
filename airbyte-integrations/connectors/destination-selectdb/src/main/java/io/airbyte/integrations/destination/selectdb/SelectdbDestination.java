/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.selectdb.http.HttpUtil;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SelectdbDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SelectdbDestination.class);

  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();
  private static HttpUtil http = new HttpUtil();
  static final String DESTINATION_TEMP_PATH_FIELD = "destination_temp_path";
  private SelectdbOperations selectdbOperations;

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new SelectdbDestination()).run(args);
  }

  public SelectdbDestination() {
    this.selectdbOperations = new SelectdbOperations();
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      Preconditions.checkNotNull(config);
      FileUtils.forceMkdir(getTempPathDir(config).toFile());
      selectdbOperations.getConn(config);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException, SQLException {
    final Map<String, SelectdbWriteConfig> writeConfigs = new HashMap<>();
    try {
      final Path destinationDir = getTempPathDir(config);
      FileUtils.forceMkdir(destinationDir.toFile());
      for (ConfiguredAirbyteStream stream : configuredCatalog.getStreams()) {

        final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
        if (syncMode == null) {
          throw new IllegalStateException("Undefined destination sync mode");
        }

        final String streamName = stream.getStream().getName();
        final String tableName = namingResolver.getIdentifier(streamName);
        final String tmpTableName = namingResolver.getTmpTableName(streamName);
        final Path tmpPath = destinationDir.resolve(tmpTableName + ".csv");

        Statement stmt = selectdbOperations.getConn(config).createStatement();
        stmt.execute(selectdbOperations.createTableQuery(tableName));
        if (syncMode == DestinationSyncMode.OVERWRITE) {
          stmt.execute(selectdbOperations.truncateTable(tableName));
        }
        CSVFormat csvFormat = CSVFormat.DEFAULT
            .withSkipHeaderRecord()
            .withDelimiter(SelectdbCopyInto.CSV_COLUMN_SEPARATOR)
            .withQuote(null)
            .withHeader(
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                JavaBaseConstants.COLUMN_NAME_DATA);
        final FileWriter fileWriter = new FileWriter(tmpPath.toFile(), Charset.defaultCharset(), false);
        final CSVPrinter printer = new CSVPrinter(fileWriter, csvFormat);
        SelectdbCopyInto sci = new SelectdbCopyInto(
            tmpPath,
            SelectdbConnectionOptions.getSelectdbConnection(config, tableName),
            new LabelInfo("", tableName),
            http.getClient(),
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA);
        writeConfigs.put(streamName, new SelectdbWriteConfig(sci, printer, csvFormat));
      }
    } catch (SQLException | ClassNotFoundException e) {
      LOGGER.error("Exception while creating Selectdb destination table: ", e);
      throw new SQLException(e);
    } catch (IOException e) {
      LOGGER.error("Exception while handling temporary csv files : ", e);
      throw new IOException(e);
    } finally {
      selectdbOperations.closeConn();
    }
    return new SelectdbConsumer(writeConfigs, configuredCatalog, outputRecordCollector);
  }

  protected Path getTempPathDir(final JsonNode config) {
    Path path = Paths.get(DESTINATION_TEMP_PATH_FIELD);
    Preconditions.checkNotNull(path);
    if (!path.startsWith("/code/local")) {
      path = Path.of("/local", path.toString());
    }
    final Path normalizePath = path.normalize();
    if (!normalizePath.startsWith("/local")) {
      throw new IllegalArgumentException("Copy into destination temp file should be inside the /local directory");
    }
    return path;
  }

}

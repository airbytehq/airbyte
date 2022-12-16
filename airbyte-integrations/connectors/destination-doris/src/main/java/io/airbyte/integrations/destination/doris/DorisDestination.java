/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import static io.airbyte.integrations.destination.doris.DorisStreamLoad.CSV_COLUMN_SEPARATOR;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
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
import java.sql.*;
import java.util.*;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DorisDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DorisDestination.class);
  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();
  private static Connection conn = null;
  private static HttpUtil http = new HttpUtil();
  static final String DESTINATION_TEMP_PATH_FIELD = "destination_temp_path";
  private static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
  private static final String DB_URL_PATTERN = "jdbc:mysql://%s:%d/%s?rewriteBatchedStatements=true&useUnicode=true&characterEncoding=utf8";

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new DorisDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      Preconditions.checkNotNull(config);
      FileUtils.forceMkdir(getTempPathDir(config).toFile());
      checkDorisAndConnect(config);
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
    final Map<String, DorisWriteConfig> writeConfigs = new HashMap<>();

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
        if (conn == null)
          checkDorisAndConnect(config);
        Statement stmt = conn.createStatement();
        stmt.execute(createTableQuery(tableName));
        if (syncMode == DestinationSyncMode.OVERWRITE) {
          stmt.execute(truncateTable(tableName));
        }
        CSVFormat csvFormat = CSVFormat.DEFAULT
            .withSkipHeaderRecord()
            .withDelimiter(CSV_COLUMN_SEPARATOR)
            .withQuote(null)
            .withHeader(
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                JavaBaseConstants.COLUMN_NAME_DATA);
        final FileWriter fileWriter = new FileWriter(tmpPath.toFile(), Charset.defaultCharset(), false);
        final CSVPrinter printer = new CSVPrinter(fileWriter, csvFormat);
        DorisStreamLoad dorisStreamLoad = new DorisStreamLoad(
            tmpPath,
            DorisConnectionOptions.getDorisConnection(config, tableName),
            new DorisLabelInfo("airbyte_doris", tableName, true),
            http.getClient(),
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA);
        writeConfigs.put(streamName, new DorisWriteConfig(dorisStreamLoad, printer, csvFormat));
      }
    } catch (SQLException | ClassNotFoundException e) {
      LOGGER.error("Exception while creating Doris destination table: ", e);
      throw new SQLException(e);
    } catch (IOException e) {
      LOGGER.error("Exception while handling temporary csv files : ", e);
      throw new IOException(e);
    } finally {
      if (conn != null)
        conn.close();
    }
    return new DorisConsumer(writeConfigs, configuredCatalog, outputRecordCollector);
  }

  protected void checkDorisAndConnect(JsonNode config) throws ClassNotFoundException, SQLException {
    DorisConnectionOptions dorisConnection = DorisConnectionOptions.getDorisConnection(config, "");
    String dbUrl = String.format(DB_URL_PATTERN, dorisConnection.getFeHost(), dorisConnection.getFeQueryPort(), dorisConnection.getDb());
    Class.forName(JDBC_DRIVER);
    conn = DriverManager.getConnection(dbUrl, dorisConnection.getUser(), dorisConnection.getPwd());
  }

  protected String createTableQuery(String tableName) {
    String s = "CREATE TABLE IF NOT EXISTS `" + tableName + "` ( \n"
        + "`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "` varchar(40),\n"
        + "`" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "` BIGINT,\n"
        + "`" + JavaBaseConstants.COLUMN_NAME_DATA + "` String)\n"
        + "DUPLICATE KEY(`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "`,`" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "`) \n"
        + "DISTRIBUTED BY HASH(`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "`) BUCKETS 16 \n"
        + "PROPERTIES ( \n"
        + "\"replication_allocation\" = \"tag.location.default: 1\" \n"
        + ");";
    LOGGER.info("create doris table SQL :  \n " + s);
    return s;
  }

  protected String truncateTable(String tableName) {
    String s = "TRUNCATE TABLE `" + tableName + "`;";
    LOGGER.info("truncate doris table SQL :  \n " + s);
    return s;
  }

  protected Path getTempPathDir(final JsonNode config) {
    Path path = Paths.get(DESTINATION_TEMP_PATH_FIELD);
    Preconditions.checkNotNull(path);
    if (!path.startsWith("/code/local")) {
      path = Path.of("/local", path.toString());
    }
    final Path normalizePath = path.normalize();
    if (!normalizePath.startsWith("/local")) {
      throw new IllegalArgumentException("Stream Load destination temp file should be inside the /local directory");
    }
    return path;
  }

}

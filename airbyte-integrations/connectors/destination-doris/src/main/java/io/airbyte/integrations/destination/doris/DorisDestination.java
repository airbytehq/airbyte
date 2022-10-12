/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.*;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DorisDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DorisDestination.class);

  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private static HttpUtil http = new HttpUtil();

  static final String DESTINATION_TEMP_PATH_FIELD = "destination_temp_path";


  public static void main(String[] args) throws Exception {


    // DorisDestination dd = new DorisDestination();



    new IntegrationRunner(new DorisDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      FileUtils.forceMkdir(getTempPathDir(config).toFile());
      checkDorisPing(config);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) throws IOException {

    final Path destinationDir = getTempPathDir(config);

    FileUtils.forceMkdir(destinationDir.toFile());

    final Map<String, DorisWriteConfig> writeConfigs = new HashMap<>();

    for (ConfiguredAirbyteStream stream : configuredCatalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final Path tmpPath = destinationDir.resolve(tmpTableName + ".csv");
      Iterator<String> properties = stream.getStream().getJsonSchema().get("properties").fieldNames();
      ArrayList<String> heads = new ArrayList<>();
      while(properties.hasNext()){
        heads.add(properties.next());
      }
      CSVFormat csvFormat = CSVFormat.DEFAULT.withSkipHeaderRecord()
              .withHeader(
                      heads.toArray(new String[]{})
              );
      final FileWriter fileWriter = new FileWriter(tmpPath.toFile(), Charset.defaultCharset(), false);
      final CSVPrinter printer = new CSVPrinter(fileWriter, csvFormat);
      DorisStreamLoad dorisStreamLoad = new DorisStreamLoad(
              tmpPath,
              DorisConnectionOptions.getDorisConnection(config, streamName),
              new DorisLabelInfo("airbyte_doris_destination", true),
              http.getClient(),
              heads
      );
      writeConfigs.put(streamName, new DorisWriteConfig(tmpPath, dorisStreamLoad, printer, csvFormat));
    }
    return new DorisConsumer(writeConfigs, configuredCatalog, outputRecordCollector);
  }




  protected void checkDorisPing(final JsonNode config) {
    // Preconditions.checkNotNull(config.get);
  }

  protected Path getTempPathDir(final JsonNode config) {
    Path path = Paths.get(DESTINATION_TEMP_PATH_FIELD);
    Preconditions.checkNotNull(path);
    if (!path.startsWith("/code/local")){
      path = Path.of("/local", path.toString());
    }
    final Path normalizePath = path.normalize();
    if (!normalizePath.startsWith("/local")) {
      throw new IllegalArgumentException("Stream Load destination temp file should be inside the /local directory");
    }
    return path;
  }

}

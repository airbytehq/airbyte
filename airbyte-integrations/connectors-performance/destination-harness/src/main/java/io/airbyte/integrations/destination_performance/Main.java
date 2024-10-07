/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Main {

  private static final Logger log = LoggerFactory.getLogger(Main.class);
  private static final String CREDENTIALS_PATH = "secrets/%s_%s_credentials.json";

  public static void main(final String[] args) {
    // If updating args for Github Actions, also update the run-harness-process.yaml and
    // connector-performance-command.yml
    log.info("args: {}", Arrays.toString(args));
    String image = null;
    String dataset = "1m";
    int numOfParallelStreams = 1;
    String syncMode = "full_refresh";

    // TODO (ryankfu): Add a better way to parse arguments. Take a look at {@link Clis.java} for
    // references
    switch (args.length) {
      case 1 -> image = args[0];
      case 2 -> {
        image = args[0];
        dataset = args[1];
      }
      case 3 -> {
        image = args[0];
        dataset = args[1];
        numOfParallelStreams = Integer.parseInt(args[2]);
      }
      case 4 -> {
        image = args[0];
        dataset = args[1];
        numOfParallelStreams = Integer.parseInt(args[2]);
        syncMode = args[3];
      }
      default -> {
        log.info("unexpected arguments");
        System.exit(1);
      }
    }

    final String connector = image.substring(image.indexOf("/") + 1, image.indexOf(":"));
    log.info("Connector name: {}", connector);
    final Path credsPath = Path.of(CREDENTIALS_PATH.formatted(connector, dataset));

    if (!Files.exists(credsPath)) {
      throw new IllegalStateException("{module-root}/" + credsPath + " not found. Must provide path to a destination-harness credentials file.");
    }

    final JsonNode config = Jsons.deserialize(IOs.readFile(credsPath));

    final JsonNode catalog;
    try {
      catalog = getCatalog(dataset, connector);
      updateSyncMode(catalog, syncMode);
      duplicateStreams(catalog, numOfParallelStreams);
    } catch (final IOException ex) {
      throw new IllegalStateException("Failed to read catalog", ex);
    }

    final String datasource;
    try {
      datasource = getDatasource(dataset, connector);
    } catch (final IOException ex) {
      throw new IllegalStateException("Failed to read datasource", ex);
    }

    if (StringUtils.isAnyBlank(config.toString(), catalog.toString(), image)) {
      throw new IllegalStateException("Missing harness configuration: config [%s] catalog [%s] image [%s]".formatted(config, catalog, image));
    }

    log.info("Starting performance harness for {} ({})", image, dataset);
    try {
      final PerformanceHarness test = new PerformanceHarness(
          image,
          config.toString(),
          catalog.toString(),
          datasource);
      test.runTest();
    } catch (final Exception e) {
      log.error("Test failed", e);
      System.exit(1);

    }
    System.exit(0);
  }

  /**
   * Modifies the catalog in place to update the syncMode to INCREMENTAL | APPEND to match CDC
   * {@link CdcMssqlSourceAcceptanceTest} for reference. If the syncMode isn't INCREMENTAL then no-op
   * since default catalog is FULL_REFERESH
   *
   * @param catalog ConfiguredCatalog to be modified
   * @param syncMode syncMode to update to
   */
  @VisibleForTesting
  static void updateSyncMode(final JsonNode catalog, final String syncMode) {
    if (syncMode.equals(SyncMode.INCREMENTAL.toString())) {
      try {
        final ObjectNode streamObject = (ObjectNode) catalog.path("streams").get(0);
        streamObject.put("sync_mode", SyncMode.INCREMENTAL.toString());
        streamObject.put("destination_sync_mode", DestinationSyncMode.APPEND.toString());
      } catch (final Exception e) {
        log.error("Failed to update sync mode", e);
      }
    }
  }

  /**
   * Duplicate the streams in the catalog to emulate parallel streams
   *
   * @param root the catalog
   * @param duplicateFactor the number of times to duplicate each stream
   */
  @VisibleForTesting
  static void duplicateStreams(final JsonNode root, final int duplicateFactor) {
    try {
      final ObjectNode streamObject = (ObjectNode) root.path("streams").get(0);
      // Since we already have one stream, we only need to duplicate the remaining streams
      for (int i = 1; i < duplicateFactor; i++) {
        final ObjectNode newStream = streamObject.deepCopy();
        final String streamName = newStream.path("stream").path("name").asText();
        ((ObjectNode) newStream.get("stream")).put("name", streamName + i);
        ((ArrayNode) root.path("streams")).add(newStream);
      }
    } catch (final Exception e) {
      log.error("Failed to duplicate streams", e);
    }
  }

  /**
   * Read the datasource file for the given dataset and connector.
   * <p>
   * Example: catalogs/destination_snowflake/1m_datasource.txt
   *
   * @param dataset the dataset to read
   * @param connector the connector to read
   * @return the datasource
   * @throws IOException if the datasource file cannot be read
   */
  static String getDatasource(final String dataset, final String connector) throws IOException {
    final String datasourceFilename = "catalogs/%s/%s_datasource.txt".formatted(connector, dataset);
    log.info("datasourceFilename {}", datasourceFilename);
    try (final var reader =
        new BufferedReader(new InputStreamReader(Objects.requireNonNull(
            Thread.currentThread().getContextClassLoader().getResourceAsStream(datasourceFilename)), StandardCharsets.UTF_8))) {
      return reader.readLine();
    }
  }

  /**
   * Read the catalog file for the given dataset and connector.
   * <p>
   * Example: catalogs/destination_snowflake/1m_catalog.json
   *
   * @param dataset the dataset to read
   * @param connector the connector to read
   * @return the catalog
   * @throws IOException if the catalog file cannot be read
   */
  static JsonNode getCatalog(final String dataset, final String connector) throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String catalogFilename = "catalogs/%s/%s_catalog.json".formatted(connector, dataset);
    final InputStream is = Thread.currentThread().getContextClassLoader().getResourceAsStream(catalogFilename);
    return objectMapper.readTree(is);
  }

}

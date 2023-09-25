/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source_performance;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

@Slf4j
public class Main {

  private static final String CREDENTIALS_PATH = "secrets/%s_%s_credentials.json";

  public static void main(final String[] args) {
    log.info("args: {}", Arrays.toString(args));
    String image = null;
    String dataset = "1m";
    // TODO: (ryankfu) add function parity with destination_performance
    int numOfParallelStreams = 1;
    String syncMode = "full_refresh";

    // TODO: (ryankfu) Integrated something akin to {@link Clis} for parsing arguments.
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
      throw new IllegalStateException("{module-root}/" + credsPath + " not found. Must provide path to a source-harness credentials file.");
    }

    final JsonNode config = Jsons.deserialize(IOs.readFile(credsPath));

    final JsonNode catalog;
    try {
      catalog = getCatalog(dataset, connector);
    } catch (final IOException ex) {
      throw new IllegalStateException("Failed to read catalog", ex);
    }

    if (StringUtils.isAnyBlank(config.toString(), catalog.toString(), image)) {
      throw new IllegalStateException("Missing harness configuration: config [%s] catalog [%s] image [%s]".formatted(config, catalog, image));
    }

    log.info("Starting performance harness for {} ({})", image, dataset);
    try {
      final PerformanceTest test = new PerformanceTest(
          image,
          config.toString(),
          catalog.toString());
      test.runTest();
    } catch (final Exception e) {
      log.error("Test failed", e);
      System.exit(1);

    }
    System.exit(0);
  }

  static JsonNode getCatalog(final String dataset, final String connector) throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String catalogFilename = "catalogs/%s/%s_catalog.json".formatted(connector, dataset);
    final InputStream is = Thread.currentThread().getContextClassLoader().getResourceAsStream(catalogFilename);
    return objectMapper.readTree(is);
  }

}

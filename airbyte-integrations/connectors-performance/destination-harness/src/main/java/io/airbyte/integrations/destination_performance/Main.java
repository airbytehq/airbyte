/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

@Slf4j
public class Main {

  private static final String CREDENTIALS_PATH = "secrets/%s_%s_credentials.json";

  public static void main(final String[] args) {
    log.info("args: {}", Arrays.toString(args));
    String image = null;
    String dataset = "1m";

    switch (args.length) {
      case 1 -> image = args[0];
      case 2 -> {
        image = args[0];
        dataset = args[1];
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
      final PerformanceTest test = new PerformanceTest(
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

  static JsonNode getCatalog(final String dataset, final String connector) throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String catalogFilename = "catalogs/%s/%s_catalog.json".formatted(connector, dataset);
    final InputStream is = Thread.currentThread().getContextClassLoader().getResourceAsStream(catalogFilename);
    return objectMapper.readTree(is);
  }

  static String getDatasource(final String dataset, final String connector) throws IOException {
    final String datasourceFilename = "catalogs/%s/%s_datasource.txt".formatted(connector, dataset);
    log.info("datasourceFilename {}", datasourceFilename);
    try (final var reader =
        new BufferedReader(new InputStreamReader(Objects.requireNonNull(
            Thread.currentThread().getContextClassLoader().getResourceAsStream(datasourceFilename)), StandardCharsets.UTF_8))) {
      return reader.readLine();
    }
  }

}

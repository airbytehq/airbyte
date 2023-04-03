/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.performance;

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

  private static final String CREDENTIALS_PATH = "secrets/%s_credentials.json";

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
    }

    final Path credsPath = Path.of(CREDENTIALS_PATH.formatted(dataset));

    if (!Files.exists(credsPath)) {
      throw new IllegalStateException("{module-root}/" + credsPath + " not found. Must provide path to a source-harness credentials file.");
    }

    final JsonNode config = Jsons.deserialize(IOs.readFile(credsPath));

    final JsonNode catalog;
    try {
      catalog = getCatalog(dataset);
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

      // final ExecutorService executors = Executors.newFixedThreadPool(2);
      // final CompletableFuture<Void> readSrcAndWriteDstThread = CompletableFuture.runAsync(() -> {
      // try {
      // test.runTest();
      // } catch (final Exception e) {
      // throw new RuntimeException(e);
      // }
      // }, executors);

      // Uncomment to add destination
      /*
       * final CompletableFuture<Void> readFromDstThread = CompletableFuture.runAsync(() -> { try {
       * Thread.sleep(20_000); test.readFromDst(); } catch (final InterruptedException e) { throw new
       * RuntimeException(e); } }, executors);
       */

      // CompletableFuture.anyOf(readSrcAndWriteDstThread/* , readFromDstThread */).get();
      test.runTest();
    } catch (final Exception e) {
      log.error("Test failed", e);
      System.exit(1);

    }
    System.exit(0);
  }

  static JsonNode getCatalog(final String dataset) throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String catalogFilename = "catalogs/%s_catalog.json".formatted(dataset);
    final InputStream is = Thread.currentThread().getContextClassLoader().getResourceAsStream(catalogFilename);
    return objectMapper.readTree(is);
  }

}

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
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

@Slf4j
public class Main {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  public static void main(final String[] args) {

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException("{module-root}/" + CREDENTIALS_PATH + " not found. Must provide path to a source-harness credentials file.");
    }

    final JsonNode config = Jsons.deserialize(IOs.readFile(CREDENTIALS_PATH));

    final JsonNode catalog;
    try {
      catalog = getCatalog();
    } catch (final IOException ex) {
      throw new IllegalStateException("Failed to read catalog", ex);
    }

    final String image = (args.length > 0) ? args[0] : "airbyte/source-postgres:dev";
    if (StringUtils.isAnyBlank(config.toString(), catalog.toString(), image)) {
      throw new IllegalStateException("Missing harness configuration");
    }

    log.info("Starting performance harness for {}", image);
    try {
      final PerformanceTest test = new PerformanceTest(
          "airbyte/source-postgres:latest",
          config.toString(),
          catalog.toString());

      final ExecutorService executors = Executors.newFixedThreadPool(2);
      final CompletableFuture<Void> readSrcAndWriteDstThread = CompletableFuture.runAsync(() -> {
        try {
          test.runTest();
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      }, executors);

      // Uncomment to add destination
      /*
       * final CompletableFuture<Void> readFromDstThread = CompletableFuture.runAsync(() -> { try {
       * Thread.sleep(20_000); test.readFromDst(); } catch (final InterruptedException e) { throw new
       * RuntimeException(e); } }, executors);
       */

      CompletableFuture.allOf(readSrcAndWriteDstThread
      /* , readFromDstThread */).get();

    } catch (final Exception e) {
      throw new RuntimeException(e);

    }
  }

  static JsonNode getCatalog() throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String catalogFilename = "catalogs/catalog.json";
    final InputStream is = Thread.currentThread().getContextClassLoader().getResourceAsStream(catalogFilename);
    return objectMapper.readTree(is);
  }

}

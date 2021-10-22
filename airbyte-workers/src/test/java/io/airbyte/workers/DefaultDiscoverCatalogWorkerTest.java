/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class DefaultDiscoverCatalogWorkerTest {

  private static final JsonNode CREDENTIALS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());
  private static final StandardDiscoverCatalogInput INPUT = new StandardDiscoverCatalogInput().withConnectionConfiguration(CREDENTIALS);

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String STREAM = "users";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_AGE = "age";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog()
      .withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
          STREAM,
          Field.of(COLUMN_NAME, JsonSchemaPrimitive.STRING),
          Field.of(COLUMN_AGE, JsonSchemaPrimitive.NUMBER))));

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory streamFactory;

  @BeforeEach
  public void setup() throws Exception {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    integrationLauncher = Mockito.mock(IntegrationLauncher.class, Mockito.RETURNS_DEEP_STUBS);
    process = Mockito.mock(Process.class);

    Mockito.when(integrationLauncher.discover(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDENTIALS)))
        .thenReturn(process);
    final InputStream inputStream = Mockito.mock(InputStream.class);
    Mockito.when(process.getInputStream()).thenReturn(inputStream);
    Mockito.when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));

    IOs.writeFile(jobRoot, WorkerConstants.SOURCE_CATALOG_JSON_FILENAME, MoreResources.readResource("airbyte_postgres_catalog.json"));

    streamFactory = noop -> Lists.newArrayList(new AirbyteMessage().withType(Type.CATALOG).withCatalog(CATALOG)).stream();
  }

  @SuppressWarnings("BusyWait")
  @Test
  public void testDiscoverSchema() throws Exception {
    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
    final AirbyteCatalog output = worker.run(INPUT, jobRoot);

    Assertions.assertThat(output).isEqualTo(CATALOG);

    org.junit.jupiter.api.Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    Mockito.verify(process).exitValue();
  }

  @SuppressWarnings("BusyWait")
  @Test
  public void testDiscoverSchemaProcessFail() throws Exception {
    Mockito.when(process.exitValue()).thenReturn(1);

    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
    Assertions.assertThatThrownBy(() -> worker.run(INPUT, jobRoot))
        .isInstanceOf(WorkerException.class)
        .hasNoCause();

    org.junit.jupiter.api.Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    Mockito.verify(process).exitValue();
  }

  @Test
  public void testDiscoverSchemaException() throws WorkerException {
    Mockito.when(integrationLauncher.discover(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDENTIALS)))
        .thenThrow(new RuntimeException());

    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
    Assertions.assertThatThrownBy(() -> worker.run(INPUT, jobRoot))
        .isInstanceOf(RuntimeException.class)
        .hasNoCause();
  }

  @Test
  public void testCancel() throws WorkerException {
    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
    worker.run(INPUT, jobRoot);

    worker.cancel();

    Mockito.verify(process).destroy();
  }

}
